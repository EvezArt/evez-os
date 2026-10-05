import { createHash } from "node:crypto";

export const EVEZ_MEDIA_TYPE = "application/vnd.evez+json";

export function parse(text) {
  const doc = JSON.parse(text);
  if (doc?.evez !== "EVEZ" || doc?.version !== 1) throw new TypeError("unsupported EVEZ document");
  return doc;
}

export function canonicalBytes(doc) {
  const copy = structuredClone(doc);
  copy.integrity = {...(copy.integrity || {})};
  delete copy.integrity.sha256;
  return Buffer.from(JSON.stringify(sortKeys(copy)));
}

function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map(k => [k, sortKeys(value[k])]));
  return value;
}

export function digest(doc) {
  return createHash("sha256").update(canonicalBytes(doc)).digest("hex");
}

export function verify(doc) {
  parse(JSON.stringify(doc));
  return typeof doc.integrity?.sha256 === "string" && doc.integrity.sha256 === digest(doc);
}

export function seal(doc) {
  const out = structuredClone(doc);
  out.integrity = {algorithm:"sha256", sha256:null};
  out.integrity.sha256 = digest(out);
  return out;
}
