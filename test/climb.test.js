import assert from "node:assert/strict";
import test from "node:test";
import { climbPressure } from "../src/climb.js";

test("empty stack is cold", () => {
  const p = climbPressure([]);
  assert.equal(p.hot, false);
  assert.equal(p.leader, null);
});

test("hot when a challenger delta clears 1.2", () => {
  const p = climbPressure([
    { ticker: "TERRACE", delta: 0.4 },
    { ticker: "LANTERN", delta: 1.8 },
  ]);
  assert.equal(p.hot, true);
  assert.equal(p.leader.ticker, "LANTERN");
});
