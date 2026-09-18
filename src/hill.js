import { climbPressure } from "./climb.js";
import { detectFall } from "./fall.js";
import { seatRead } from "./seat.js";
import { inWindow, windowBand } from "./window.js";

export function readHill({ king, climbers = [], prevKing = null } = {}) {
  if (!king) {
    return { event: "SEAT", note: "no king", window: false, send: false };
  }

  const fall = detectFall(prevKing, king);
  if (fall) {
    return {
      event: "FALL",
      note: `${fall.from} lost the hill`,
      window: inWindow(king.fill),
      band: windowBand(king.fill),
      fall,
      send: false,
    };
  }

  const climb = climbPressure(climbers);
  if (climb.hot) {
    return {
      event: "CLIMB",
      note: `${climb.leader.ticker} eating the curve`,
      window: inWindow(king.fill),
      band: windowBand(king.fill),
      climb,
      send: false,
    };
  }

  const seat = seatRead(king);
  return {
    event: "SEAT",
    note: seat.ok ? `${king.ticker} holds the hill` : `${king.ticker} ${seat.reason}`,
    window: inWindow(king.fill),
    band: windowBand(king.fill),
    seat,
    send: false,
  };
}
