import { RULES } from "./rules.js";

export function seatRead({ seatSec, fill }) {
  if (seatSec < RULES.seatMinSec) {
    return { ok: false, reason: "too_raw", seatSec };
  }
  if (seatSec > RULES.seatMaxSec) {
    return { ok: false, reason: "stale", seatSec };
  }
  return {
    ok: true,
    reason: "seated",
    seatSec,
    fill,
  };
}

export function formatSeat(seatSec) {
  const s = Math.max(0, Math.floor(seatSec));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
}
