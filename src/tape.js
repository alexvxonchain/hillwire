export const START = {
  king: { ticker: "RIDGE", ca: "7Rk…w2n", fill: 68.4, seatSec: 94, mcap: 18.4 },
  climbers: [
    { ticker: "LANTERN", fill: 64.1, delta: 1.8 },
    { ticker: "TERRACE", fill: 61.0, delta: 0.6 },
    { ticker: "SPOIL", fill: 58.4, delta: -0.4 },
  ],
};

export function at(t) {
  const king = { ...START.king };
  const climbers = START.climbers.map((c) => ({ ...c }));
  let event = "SEAT";
  let note = "RIDGE holds the hill";

  if (t < 22) {
    king.fill = 68.4 + t * 0.48;
    king.seatSec = 94 + t;
    climbers[0].fill = 64.1 + t * 0.72;
    climbers[0].delta = 1.8 + t * 0.08;
    climbers[1].fill = 61.0 + t * 0.22;
    if (t > 12) {
      event = "CLIMB";
      note = "LANTERN eating the curve";
    }
  } else if (t < 26.5) {
    event = "FALL";
    note = "hill flipped · RIDGE lost the chair";
    king.ticker = "RIDGE";
    king.fill = 78.2 - (t - 22) * 4.1;
    king.seatSec = 116;
    climbers[0].fill = 80.2 + (t - 22) * 0.9;
  } else {
    event = "SEAT";
    note = "LANTERN sat down";
    king.ticker = "LANTERN";
    king.ca = "9pQ…m4c";
    king.fill = 81.4 + (t - 26.5) * 0.18;
    king.seatSec = t - 26.5;
    king.mcap = 24.1;
    climbers[0] = { ticker: "RIDGE", fill: 76.8, delta: -2.4 };
    climbers[1] = { ticker: "TERRACE", fill: 66.2, delta: 0.3 };
    climbers[2] = { ticker: "BRINE", fill: 63.9, delta: 1.1 };
  }

  king.fill = clamp(king.fill, 4, 96);
  for (const c of climbers) c.fill = clamp(c.fill, 4, 96);
  return { king, climbers, event, note, window: king.fill >= 62 && king.fill <= 91 };
}

function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}
