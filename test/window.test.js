import assert from "node:assert/strict";
import test from "node:test";
import { inWindow, windowBand } from "../src/window.js";

test("curve under 62 is noise", () => {
  assert.equal(windowBand(40), "NOISE");
  assert.equal(inWindow(40), false);
});

test("62-91 is the hill window", () => {
  assert.equal(windowBand(62), "HILL");
  assert.equal(windowBand(91), "HILL");
  assert.equal(inWindow(74), true);
});

test("above 91 is already a screenshot", () => {
  assert.equal(windowBand(96), "SCREEN");
  assert.equal(inWindow(96), false);
});
