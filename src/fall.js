import { RULES } from "./rules.js";

export function detectFall(prevKing, nextKing) {
  if (!prevKing || !nextKing) return null;
  if (prevKing.ticker !== nextKing.ticker) {
    return {
      event: "FALL",
      from: prevKing.ticker,
      to: nextKing.ticker,
      reason: "throne_changed",
    };
  }
  const drop = (prevKing.fill || 0) - (nextKing.fill || 0);
  if (drop >= RULES.fallFillDrop) {
    return {
      event: "FALL",
      from: prevKing.ticker,
      to: nextKing.ticker,
      reason: "fill_broke",
      drop,
    };
  }
  return null;
}
