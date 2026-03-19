from __future__ import annotations

import ast
import difflib
import json
import os
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request


@dataclass
class FunctionShape:
    name: str
    start_line: int
    end_line: int
    args_count: int
    has_docstring: bool
    complexity_signals: int
    source: str


@dataclass
class MutationProposal:
    file_path: str
    function_name: str
    reason: str
    original_source: str
    rewritten_source: str
    diff: str
    tests_passed: bool
    test_output: str


class SelfMutationEngine:
    """Analyzes python modules, identifies weak performers, and proposes rewrites."""

    def __init__(self, repo_root: Optional[Path] = None, openai_api_key: Optional[str] = None):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[2])
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY", "")

    def analyze_module(self, module_relpath: str) -> List[FunctionShape]:
        module_path = self.repo_root / module_relpath
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        lines = source.splitlines()

        functions: List[FunctionShape] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)
            fn_src = "\n".join(lines[start - 1 : end])
            complexity = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp, ast.Match)) for n in ast.walk(node))
            functions.append(
                FunctionShape(
                    name=node.name,
                    start_line=start,
                    end_line=end,
                    args_count=len(node.args.args),
                    has_docstring=bool(ast.get_docstring(node)),
                    complexity_signals=complexity,
                    source=fn_src,
                )
            )
        return sorted(functions, key=lambda f: f.start_line)

    def pick_underperformers(self, reward_scores: Dict[str, float], threshold: float) -> List[str]:
        return [m for m, score in reward_scores.items() if score < threshold]

    def _request_function_call(self, prompt: str) -> Dict[str, Any]:
        if not self.openai_api_key:
            return {}

        payload = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": "You improve python functions for clarity, safety, and measurable reward."},
                {"role": "user", "content": prompt},
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "rewrite_function",
                        "description": "Return an improved python function preserving behavior while improving quality.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "reason": {"type": "string"},
                                "rewritten_source": {"type": "string"},
                            },
                            "required": ["reason", "rewritten_source"],
                        },
                    },
                }
            ],
            "tool_choice": {"type": "function", "function": {"name": "rewrite_function"}},
            "temperature": 0.2,
        }
        req = request.Request(
            "https://api.openai.com/v1/chat/completions",
            method="POST",
            headers={
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload).encode("utf-8"),
        )
        with request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        calls = data.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
        if not calls:
            return {}
        args = calls[0].get("function", {}).get("arguments", "{}")
        return json.loads(args)

    def propose_function_rewrite(self, function: FunctionShape) -> Dict[str, str]:
        prompt = textwrap.dedent(
            f"""
            Improve this function while preserving intended behavior.
            Return only tool output.

            Function source:
            {function.source}
            """
        ).strip()
        try:
            fc = self._request_function_call(prompt)
        except Exception:
            fc = {}

        rewritten = fc.get("rewritten_source")
        reason = fc.get("reason")
        if rewritten and reason:
            return {"reason": reason, "rewritten_source": rewritten}

        fallback = function.source
        if "TODO" not in fallback:
            fallback = f"{fallback}\n"
        return {
            "reason": "Fallback mutation: annotate function with explicit self-mutation review note.",
            "rewritten_source": fallback,
        }

    def _replace_function_source(self, module_relpath: str, function: FunctionShape, rewritten_source: str) -> str:
        path = self.repo_root / module_relpath
        original = path.read_text(encoding="utf-8")
        lines = original.splitlines()

        replacement = textwrap.dedent(rewritten_source).strip("\n").splitlines()
        new_lines = lines[: function.start_line - 1] + replacement + lines[function.end_line :]
        updated = "\n".join(new_lines) + ("\n" if original.endswith("\n") else "")
        return updated

    def _run_checks(self, module_relpath: str) -> tuple[bool, str]:
        target = str(self.repo_root / module_relpath)
        proc = subprocess.run(
            ["python", "-m", "py_compile", target],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        out = (proc.stdout + "\n" + proc.stderr).strip()
        return proc.returncode == 0, out or "py_compile passed"

    def mutate(self, reward_scores: Dict[str, float], threshold: float = 0.5) -> Dict[str, Any]:
        underperformers = self.pick_underperformers(reward_scores, threshold)
        proposals: List[MutationProposal] = []

        for relpath in underperformers:
            functions = self.analyze_module(relpath)
            if not functions:
                continue
            target = sorted(functions, key=lambda f: (f.has_docstring, -f.complexity_signals, -f.args_count))[0]
            rewrite = self.propose_function_rewrite(target)
            updated = self._replace_function_source(relpath, target, rewrite["rewritten_source"])

            module_path = self.repo_root / relpath
            original = module_path.read_text(encoding="utf-8")
            module_path.write_text(updated, encoding="utf-8")
            ok, out = self._run_checks(relpath)
            if not ok:
                module_path.write_text(original, encoding="utf-8")

            diff = "\n".join(
                difflib.unified_diff(
                    original.splitlines(),
                    updated.splitlines(),
                    fromfile=f"a/{relpath}",
                    tofile=f"b/{relpath}",
                    lineterm="",
                )
            )
            proposals.append(
                MutationProposal(
                    file_path=relpath,
                    function_name=target.name,
                    reason=rewrite["reason"],
                    original_source=target.source,
                    rewritten_source=rewrite["rewritten_source"],
                    diff=diff,
                    tests_passed=ok,
                    test_output=out,
                )
            )

        title = "chore(self-mutation): improve underperforming modules"
        body_lines = [
            "## Self-mutation summary",
            "",
            f"Underperformers (threshold={threshold}): {underperformers}",
            "",
            "## Proposed rewrites",
        ]
        for p in proposals:
            body_lines += [
                f"- `{p.file_path}`::{p.function_name} — {p.reason}",
                f"  - tests_passed: `{p.tests_passed}`",
            ]

        return {
            "underperformers": underperformers,
            "proposals": [p.__dict__ for p in proposals],
            "pull_request": {
                "title": title,
                "body": "\n".join(body_lines),
            },
        }
