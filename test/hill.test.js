import assert from "node:assert/strict";
import test from "node:test";
import { readHill } from "../src/hill.js";
import { refuseSend, tick, createDesk } from "../src/runtime.js";

test("paper desk never sends", () => {
  assert.equal(refuseSend().send, false);
  const desk = createDesk({
    king: { ticker: "RIDGE", fill: 70, seatSec: 94 },
    climbers: [{ ticker: "LANTERN", delta: 2.1 }],
  });
  const once = tick(desk);
  assert.equal(once.send, false);
});

test("climb beats seat when pressure is hot", () => {
  const read = readHill({
    king: { ticker: "RIDGE", fill: 70, seatSec: 94 },
    climbers: [{ ticker: "LANTERN", delta: 2.4 }],
  });
  assert.equal(read.event, "CLIMB");
  assert.equal(read.send, false);
});
