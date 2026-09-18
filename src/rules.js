export const RULES = Object.freeze({
  curveMin: 62,
  curveMax: 91,
  seatMinSec: 50,
  seatMaxSec: 16 * 60,
  climbDelta: 1.2,
  fallFillDrop: 4,
});

export function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}
