import { readHill } from "./hill.js";

export function createDesk(seed = {}) {
  return {
    prevKing: null,
    king: seed.king || null,
    climbers: seed.climbers || [],
    send: false,
  };
}

export function tick(desk) {
  const read = readHill({
    king: desk.king,
    climbers: desk.climbers,
    prevKing: desk.prevKing,
  });
  desk.prevKing = desk.king ? { ...desk.king } : null;
  return {
    ...read,
    send: false,
  };
}

export function refuseSend() {
  return { send: false, reason: "paper_desk" };
}
