import { RULES } from "./rules.js";

export function inWindow(fill) {
  return fill >= RULES.curveMin && fill <= RULES.curveMax;
}

export function windowBand(fill) {
  if (fill < RULES.curveMin) return "NOISE";
  if (fill > RULES.curveMax) return "SCREEN";
  return "HILL";
}
