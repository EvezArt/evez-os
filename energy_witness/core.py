"""Experimental meter-attestation and append-only energy evidence ledger.
HMAC is for local prototype tests only. Production requires vendor/utility
public-key signatures and independently verified settlement records. No funds
or redeemable tokens are created here.
"""
from __future__ import annotations
import hashlib, hmac, json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

class VerificationError(ValueError):
    """A reading failed an evidence or meter-policy check."""

def canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sign_reading(reading: dict[str, Any], secret: bytes) -> str:
    """Prototype-only HMAC helper; never embed secrets in the repository."""
    unsigned = {k: v for k, v in reading.items() if k != "signature"}
    return hmac.new(secret, canonical_bytes(unsigned), hashlib.sha256).hexdigest()

@dataclass(frozen=True)
class Meter:
    meter_id: str
    operator_id: str
    secret: bytes
    status: str
    calibrated_at: str
    calibration_valid_until: str

class EnergyWitness:
    def __init__(self, ledger_path: str | Path, meters: dict[str, Meter]):
        self.ledger_path, self.meters = Path(ledger_path), meters
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _time(value: str) -> datetime:
        try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc: raise VerificationError("timestamp must be ISO-8601") from exc
        if parsed.tzinfo is None: raise VerificationError("timestamp must include a timezone")
        return parsed.astimezone(timezone.utc)

    def _existing(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists(): return []
        return [json.loads(line) for line in self.ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def submit(self, reading: dict[str, Any]) -> dict[str, Any]:
        required = {"reading_id","meter_id","operator_id","interval_start","interval_end","export_wh","cumulative_export_wh","evidence_source","signature"}
        missing = required - reading.keys()
        if missing: raise VerificationError("missing fields: " + ", ".join(sorted(missing)))
        meter = self.meters.get(str(reading["meter_id"]))
        if meter is None or meter.status != "active": raise VerificationError("meter is not registered and active")
        if reading["operator_id"] != meter.operator_id: raise VerificationError("operator does not match meter registry")
        now = datetime.now(timezone.utc)
        if self._time(meter.calibrated_at) > now or self._time(meter.calibration_valid_until) < now:
            raise VerificationError("meter calibration is not currently valid")
        start, end = self._time(reading["interval_start"]), self._time(reading["interval_end"])
        if end <= start or end > now: raise VerificationError("invalid or future measurement interval")
        if reading["evidence_source"] not in {"certified_meter_attestation","utility_settlement"}:
            raise VerificationError("evidence source is not an accepted production class")
        try: export_wh, cumulative = int(reading["export_wh"]), int(reading["cumulative_export_wh"])
        except (TypeError, ValueError) as exc: raise VerificationError("energy values must be integer watt-hours") from exc
        if export_wh <= 0 or cumulative < export_wh: raise VerificationError("export must be positive and cumulative export plausible")
        expected = sign_reading(reading, meter.secret)
        if not hmac.compare_digest(str(reading["signature"]), expected): raise VerificationError("meter attestation signature is invalid")
        rows = self._existing()
        if any(row["reading_id"] == reading["reading_id"] for row in rows): raise VerificationError("duplicate reading_id; no second credit")
        prior = [r for r in rows if r["meter_id"] == meter.meter_id]
        if prior:
            latest = max(prior, key=lambda r: r["interval_end"])
            if cumulative <= int(latest["cumulative_export_wh"]): raise VerificationError("cumulative meter register did not increase")
            if start < self._time(latest["interval_end"]): raise VerificationError("overlapping or out-of-order meter interval")
        record = {"record_type":"VERIFIED_ENERGY_EVIDENCE","reading_id":str(reading["reading_id"]),
          "meter_id":meter.meter_id,"operator_id":meter.operator_id,"interval_start":start.isoformat(),
          "interval_end":end.isoformat(),"export_wh":export_wh,"export_kwh":export_wh/1000,
          "cumulative_export_wh":cumulative,"evidence_source":reading["evidence_source"],
          "verification":"prototype_attestation_passed",
          "reward_status":"NOT_ISSUED_PENDING_INDEPENDENT_SETTLEMENT",
          "previous_hash":rows[-1]["record_hash"] if rows else "0"*64}
        record["record_hash"] = hashlib.sha256(canonical_bytes(record)).hexdigest()
        with self.ledger_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        return record
