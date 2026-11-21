#!/usr/bin/env python3
"""EVEZ-OS Invariance Battery — Runtime invariant verification on port 9115."""

import ast
import operator
import json
import time
import random
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

SPINE_URL = "http://localhost:9116/append"

def spine_log(domain, action, data):
    try:
        requests.post(SPINE_URL, json={"domain": domain, "action": action, "data": data, "timestamp": time.time()}, timeout=2)
    except Exception:
        pass

# ── State ────────────────────────────────────────────────────────────

class InvarianceState:
    def __init__(self):
        self.lock = threading.Lock()
        self.invariants = {}   # id → invariant
        self.state = {}        # current system state (mutable)
        self.audit_log = []
        self._iid = 0

    def next_iid(self):
        self._iid += 1
        return f"inv-{self._iid:04d}"

STATE = InvarianceState()

# ── Invariant Management ────────────────────────────────────────────

def add_invariant(name, expression, description=""):
    """Add an invariant — a property that must ALWAYS hold."""
    with STATE.lock:
        iid = STATE.next_iid()
        inv = {
            "id": iid,
            "name": name,
            "expression": expression,
            "description": description,
            "created": time.time(),
            "check_count": 0,
            "fail_count": 0,
            "last_result": None,
            "last_check": None,
        }
        STATE.invariants[iid] = inv
    spine_log("invariance", "assert", {"id": iid, "name": name})
    return inv

def evaluate_expression(expression, state):
    """Evaluate a restricted invariant language without eval()/exec()."""
    try:
        if not isinstance(expression, str) or len(expression) > 2000:
            raise ValueError("expression must be a string <= 2000 characters")
        tree = ast.parse(expression, mode="eval")
        calls = {
            "len": len, "abs": abs, "min": min, "max": max,
            "sum": sum, "any": any, "all": all,
            "isinstance": isinstance, "int": int, "float": float,
            "str": str, "bool": bool, "list": list, "dict": dict,
            "round": round,
        }
        binops = {
            ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod, ast.Pow: operator.pow,
        }
        cmpops = {
            ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
            ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
            ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
            ast.Is: operator.is_, ast.IsNot: operator.is_not,
        }
        unops = {ast.Not: operator.not_, ast.USub: operator.neg, ast.UAdd: operator.pos}

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (str, int, float, bool, type(None))):
                    return node.value
                raise ValueError("constant type not allowed")
            if isinstance(node, ast.Name):
                if node.id == "state":
                    return state
                if node.id in calls:
                    return calls[node.id]
                raise ValueError(f"name not allowed: {node.id}")
            if isinstance(node, ast.Attribute):
                base = visit(node.value)
                if node.attr == "get" and isinstance(base, dict):
                    return base.get
                raise ValueError("only dict.get is allowed")
            if isinstance(node, ast.Call):
                fn = visit(node.func)
                if fn not in calls.values() and fn != state.get:
                    raise ValueError("call not allowed")
                args = [visit(x) for x in node.args]
                kwargs = {x.arg: visit(x.value) for x in node.keywords}
                return fn(*args, **kwargs)
            if isinstance(node, ast.Subscript):
                return visit(node.value)[visit(node.slice)]
            if isinstance(node, ast.List):
                return [visit(x) for x in node.elts]
            if isinstance(node, ast.Tuple):
                return tuple(visit(x) for x in node.elts)
            if isinstance(node, ast.Dict):
                return {visit(k): visit(v) for k, v in zip(node.keys, node.values)}
            if isinstance(node, ast.BoolOp):
                if isinstance(node.op, ast.And):
                    for x in node.values:
                        if not visit(x):
                            return False
                    return True
                if isinstance(node.op, ast.Or):
                    for x in node.values:
                        if visit(x):
                            return True
                    return False
                raise ValueError("boolean operator not allowed")
            if isinstance(node, ast.BinOp) and type(node.op) in binops:
                return binops[type(node.op)](visit(node.left), visit(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in unops:
                return unops[type(node.op)](visit(node.operand))
            if isinstance(node, ast.Compare):
                left = visit(node.left)
                for op_node, right_node in zip(node.ops, node.comparators):
                    if type(op_node) not in cmpops:
                        raise ValueError("comparison operator not allowed")
                    right = visit(right_node)
                    if not cmpops[type(op_node)](left, right):
                        return False
                    left = right
                return True
            raise ValueError(f"syntax not allowed: {type(node).__name__}")

        return bool(visit(tree)), None
    except (SyntaxError, ValueError, TypeError, KeyError, IndexError, ZeroDivisionError, OverflowError) as e:
        return False, str(e)

def check_all():
    """Check ALL invariants against current state. Falsification over verification."""
    results = []
    with STATE.lock:
        state = dict(STATE.state)
        invariants = dict(STATE.invariants)

    for iid, inv in invariants.items():
        passed, error = evaluate_expression(inv["expression"], state)
        with STATE.lock:
            STATE.invariants[iid]["check_count"] += 1
            STATE.invariants[iid]["last_check"] = time.time()
            STATE.invariants[iid]["last_result"] = passed
            if not passed:
                STATE.invariants[iid]["fail_count"] += 1
        results.append({
            "invariant_id": iid,
            "name": inv["name"],
            "passed": passed,
            "error": error,
        })

    all_pass = all(r["passed"] for r in results)
    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "all_hold": all_pass,
        "results": results,
        "timestamp": time.time(),
    }
    STATE.audit_log.append(summary)
    if len(STATE.audit_log) > 100:
        STATE.audit_log = STATE.audit_log[-100:]
    spine_log("invariance", "check", {"all_hold": all_pass, "failed": summary["failed"]})
    return summary

def falsify_invariant(iid):
    """Attempt to break an invariant by generating adversarial state mutations."""
    with STATE.lock:
        inv = STATE.invariants.get(iid)
        state = dict(STATE.state)

    if not inv:
        return {"error": "invariant not found"}

    # Strategy: try various mutations to break the invariant
    mutations_tried = []
    falsified = False

    # Mutation strategies
    strategies = [
        ("zero_state", lambda s: {k: 0 if isinstance(v, (int, float)) else v for k, v in s.items()}),
        ("max_values", lambda s: {k: 999999 if isinstance(v, (int, float)) else v for k, v in s.items()}),
        ("negate_bools", lambda s: {k: not v if isinstance(v, bool) else v for k, v in s.items()}),
        ("empty_collections", lambda s: {k: [] if isinstance(v, list) else {} if isinstance(v, dict) else v for k, v in s.items()}),
        ("nullify", lambda s: {k: None for k in s}),
        ("random_noise", lambda s: {k: v + random.uniform(-100, 100) if isinstance(v, (int, float)) else v for k, v in s.items()}),
    ]

    for strat_name, mutator in strategies:
        try:
            mutated = mutator(dict(state))
            passed, error = evaluate_expression(inv["expression"], mutated)
            mutations_tried.append({"strategy": strat_name, "passed": passed, "error": error})
            if not passed:
                falsified = True
                break
        except Exception as e:
            mutations_tried.append({"strategy": strat_name, "error": str(e)})

    result = {
        "invariant_id": iid,
        "name": inv["name"],
        "falsified": falsified,
        "mutations_tried": len(mutations_tried),
        "details": mutations_tried,
        "verdict": "BROKEN" if falsified else "HELD",
    }
    spine_log("invariance", "falsify", {"id": iid, "falsified": falsified})
    return result

def full_audit():
    """Complete audit of all invariants."""
    check_result = check_all()
    with STATE.lock:
        invariants = {k: v for k, v in STATE.invariants.items()}

    falsifications = []
    for iid in invariants:
        falsifications.append(falsify_invariant(iid))

    return {
        "check": check_result,
        "falsifications": falsifications,
        "invariants": invariants,
        "audit_time": time.time(),
        "verdict": "PASS" if check_result["all_hold"] and not any(f["falsified"] for f in falsifications) else "FAIL",
    }

# ── HTTP Handler ─────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "invariance", "port": 9115})
        elif self.path == "/invariants":
            with STATE.lock:
                invs = {k: v for k, v in STATE.invariants.items()}
            self._json(200, {"invariants": invs, "count": len(invs)})
        elif self.path == "/state":
            with STATE.lock:
                s = dict(STATE.state)
            self._json(200, {"state": s})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "invariance", "port": 9115})
            return

        body = self._read_body()

        if self.path == "/assert":
            name = body.get("name")
            expression = body.get("expression")
            if not name or not expression:
                self._json(400, {"error": "name and expression required"})
                return
            inv = add_invariant(name, expression, body.get("description", ""))
            self._json(201, inv)
        elif self.path == "/check":
            result = check_all()
            self._json(200, result)
        elif self.path == "/falsify":
            iid = body.get("invariant_id")
            if not iid:
                # Falsify all
                with STATE.lock:
                    iids = list(STATE.invariants.keys())
                results = [falsify_invariant(i) for i in iids]
                self._json(200, {"results": results})
            else:
                result = falsify_invariant(iid)
                self._json(200, result)
        elif self.path == "/audit":
            result = full_audit()
            self._json(200, result)
        elif self.path == "/state":
            # Update state
            with STATE.lock:
                STATE.state.update(body)
            self._json(200, {"state": STATE.state})
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9115), Handler)
    print("Invariance Battery running on :9115")
    server.serve_forever()
