import { RULES } from "./rules.js";

export function climbPressure(climbers = []) {
  if (!climbers.length) {
    return { hot: false, leader: null, delta: 0 };
  }
  const ranked = [...climbers].sort((a, b) => (b.delta || 0) - (a.delta || 0));
  const leader = ranked[0];
  const delta = Number(leader.delta || 0);
  return {
    hot: delta >= RULES.climbDelta,
    leader,
    delta,
  };
}
