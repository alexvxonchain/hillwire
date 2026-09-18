import assert from "node:assert/strict";
import test from "node:test";
import { formatSeat, seatRead } from "../src/seat.js";

test("rejects a king younger than 50s", () => {
  const read = seatRead({ seatSec: 12, fill: 70 });
  assert.equal(read.ok, false);
  assert.equal(read.reason, "too_raw");
});

test("rejects a king older than 16m", () => {
  const read = seatRead({ seatSec: 20 * 60, fill: 70 });
  assert.equal(read.ok, false);
  assert.equal(read.reason, "stale");
});

test("formats seat clock", () => {
  assert.equal(formatSeat(94), "01:34");
});
