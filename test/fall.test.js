import assert from "node:assert/strict";
import test from "node:test";
import { detectFall } from "../src/fall.js";

test("ticker change is a fall", () => {
  const fall = detectFall(
    { ticker: "RIDGE", fill: 78 },
    { ticker: "LANTERN", fill: 81 }
  );
  assert.equal(fall.event, "FALL");
  assert.equal(fall.from, "RIDGE");
  assert.equal(fall.to, "LANTERN");
});

test("same king is not a fall", () => {
  const fall = detectFall(
    { ticker: "RIDGE", fill: 70 },
    { ticker: "RIDGE", fill: 71 }
  );
  assert.equal(fall, null);
});
