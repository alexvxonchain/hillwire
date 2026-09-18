"""HILLWIRE desk clip: dense $ tape, live ticks, 40s beat."""
from __future__ import annotations

import math
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "frames"
ASSETS = ROOT / "assets"
OUT = ASSETS / "hillwire.mp4"
STILL = ASSETS / "desk.png"
WAV = ASSETS / "bed.wav"

W, H, FPS, SECS = 1280, 720, 30, 40
BPM = 150
BEAT = 60.0 / BPM
DROP = 8.0
BG = (10, 9, 8)
PANEL = (18, 16, 14)
LINE = (48, 40, 32)
COPPER = (208, 138, 76)
CREAM = (240, 230, 216)
MUTE = (130, 118, 104)
FALL = (214, 78, 58)
UP = (180, 196, 92)
DIM = (28, 24, 20)

BOOKS = [
    ("RIDGE", 48210, 1.8, 71, "SEAT"),
    ("LANTERN", 191004, 12.4, 84, "CLIMB"),
    ("TERRACE", 63880, -2.1, 66, "SEAT"),
    ("SPOIL", 12440, -8.6, 41, "FALL"),
    ("BRINE", 274330, 4.7, 79, "CLIMB"),
    ("WICK", 8902, 22.0, 58, "CLIMB"),
    ("GROVE", 156710, 0.6, 73, "SEAT"),
    ("ASH", 33190, -14.2, 38, "FALL"),
    ("CINDER", 72105, 3.3, 69, "SEAT"),
    ("MARSH", 4418, 31.5, 52, "CLIMB"),
    ("QUARRY", 98060, -1.4, 64, "SEAT"),
    ("FOLD", 210884, 7.9, 88, "CLIMB"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)
    except OSError:
        return ImageFont.load_default()


F_BRAND = font(22, True)
F_DOLLAR = font(28, True)
F_BIG = font(42, True)
F_META = font(15)
F_SM = font(12)
F_TINY = font(11)
F_TAPE = font(13, True)
F_BOOT = font(72, True)


def money(n: float) -> str:
    n = int(round(n))
    if n >= 1_000_000:
        return f" ${n / 1_000_000:.2f}M"
    return f" ${n:,}"


def tick_book(i: int, t: float) -> dict:
    name, base, pct0, curve0, tag = BOOKS[i]
    wobble = 0.018 * math.sin(t * 9.4 + i * 1.7) + 0.007 * math.sin(t * 27 + i)
    drift = 1 + 0.004 * t * (1 if pct0 > 0 else -0.6)
    if t >= 22 and name == "RIDGE":
        tag = "FALL"
        pct0 = -11.4
        drift = 0.82
    if t >= 26.5 and name == "LANTERN":
        tag = "SEAT"
    mcap = max(900, base * drift * (1 + wobble))
    pct = pct0 + 3.2 * math.sin(t * 2.4 + i) + (8 if tag == "CLIMB" else 0) * 0.15 * math.sin(t * 5)
    curve = max(8, min(96, curve0 + 4 * math.sin(t * 0.8 + i * 0.4) + (0.35 * t if tag == "CLIMB" else 0)))
    return {"name": name, "mcap": mcap, "pct": pct, "curve": curve, "tag": tag}


def king_at(t: float) -> dict:
    if t < 22:
        b = tick_book(0, t)
        return {"name": "RIDGE", "sol": 3.84 + t * 0.031, "usd": b["mcap"], "pnl": 318 + t * 22, "last": 31 + t * 1.4}
    if t < 26.5:
        b = tick_book(0, t)
        return {"name": "RIDGE", "sol": 2.10 - (t - 22) * 0.18, "usd": b["mcap"], "pnl": 840 - (t - 22) * 90, "last": -214}
    b = tick_book(1, t)
    return {
        "name": "LANTERN",
        "sol": 4.12 + (t - 26.5) * 0.05,
        "usd": b["mcap"],
        "pnl": 1840 + (t - 26.5) * 70,
        "last": 126 + (t - 26.5) * 8,
    }


def punch(img: Image.Image, t: float, kick: float) -> Image.Image:
    beat_i = int(t / BEAT)
    snare = beat_i % 2 == 1
    drop = t >= DROP
    z = 1.0 + (0.085 if drop else 0.04) * kick
    if drop and snare:
        z += 0.03 * kick
    z = min(z, 1.16)
    nw, nh = int(W / z), int(H / z)
    x = (W - nw) // 2
    y = int((H - nh) * 0.42)
    img = img.crop((x, y, x + nw, y + nh)).resize((W, H), Image.Resampling.BILINEAR)
    if drop and kick > 0.55:
        flash = Image.new("RGB", (W, H), (255, 230, 200) if snare else COPPER)
        img = Image.blend(img, flash, 0.07 * kick)
    return img


def frame(t: float) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # First frames stay on the live desk so X/Twitter preview is the terminal, not a title card.

    k = king_at(t)
    books = [tick_book(i, t) for i in range(12)]
    kick = math.exp(-((t / BEAT) % 1.0) * 14)
    pulse = kick

    d.rectangle((0, 0, W, 42), fill=(16, 14, 12))
    d.text((16, 12), "HILLWIRE", font=F_BRAND, fill=CREAM)
    d.text((148, 16), "PUMP.FUN HILL DESK  ·  ALEXYZ  ·  PAPER", font=F_SM, fill=MUTE)
    last_col = UP if k["last"] >= 0 else FALL
    d.text((700, 16), f"LAST HILL {money(k['last'])}", font=F_SM, fill=last_col)
    d.text((920, 16), f"+PNL {money(k['pnl'])}", font=F_SM, fill=UP if k["pnl"] >= 0 else FALL)
    d.text((1264, 16), f"00:{int(t):02d}", font=F_SM, fill=MUTE, anchor="rt")
    d.line((0, 42, W, 42), fill=COPPER if pulse > 0.7 else LINE)

    # 4x3 dollar cards
    gap, cw, ch = 8, 188, 118
    ox, oy = 14, 54
    for i, b in enumerate(books):
        col, row = i % 4, i // 4
        x, y = ox + col * (cw + gap), oy + row * (ch + gap)
        d.rectangle((x, y, x + cw, y + ch), fill=PANEL, outline=LINE)
        tag_col = {"SEAT": COPPER, "CLIMB": UP, "FALL": FALL}[b["tag"]]
        d.text((x + 10, y + 8), b["name"], font=F_SM, fill=MUTE)
        d.text((x + cw - 10, y + 8), "pump.fun", font=F_TINY, fill=(90, 80, 70), anchor="rt")
        dol_col = CREAM if b["pct"] >= 0 else FALL
        d.text((x + 10, y + 32), money(b["mcap"]).strip(), font=F_DOLLAR, fill=dol_col)
        sign = "+" if b["pct"] >= 0 else ""
        d.text((x + 10, y + 68), f"{sign}{b['pct']:.1f}%", font=F_SM, fill=UP if b["pct"] >= 0 else FALL)
        d.text((x + cw - 10, y + 68), b["tag"], font=F_TINY, fill=tag_col, anchor="rt")
        d.rectangle((x + 10, y + ch - 16, x + cw - 10, y + ch - 10), fill=DIM)
        d.rectangle((x + 10, y + ch - 16, x + 10 + int((cw - 20) * b["curve"] / 100), y + ch - 10), fill=COPPER)

    # right king stack
    rx = 790
    d.rectangle((rx, 54, 1266, 300), fill=PANEL, outline=LINE)
    d.text((rx + 16, 66), "LOOKING AT", font=F_TINY, fill=MUTE)
    d.text((rx + 16, 84), k["name"], font=F_BIG, fill=CREAM)
    d.text((1250, 70), "HILL", font=F_TINY, fill=COPPER, anchor="rt")
    d.text((rx + 16, 140), f"{k['sol']:.3f} SOL", font=F_DOLLAR, fill=COPPER)
    d.text((rx + 16, 178), money(k["usd"]).strip(), font=F_BIG, fill=CREAM)
    d.text((rx + 16, 232), f"session {money(k['pnl']).strip()}", font=F_META, fill=UP if k["pnl"] >= 0 else FALL)
    d.text((rx + 16, 262), "paper  ·  no keys  ·  nothing sends", font=F_TINY, fill=MUTE)

    # volume
    d.rectangle((rx, 310, 1266, 430), fill=PANEL, outline=LINE)
    d.text((rx + 16, 320), "VOLUME", font=F_TINY, fill=MUTE)
    for i in range(22):
        accent = 1.0 if i % 4 == 0 else 0.55
        hgt = 10 + (18 + 78 * kick) * accent * (0.7 + 0.3 * math.sin(t * 3 + i))
        x0 = rx + 18 + i * 21
        col = COPPER if i % 2 == 0 else UP
        d.rectangle((x0, 410 - hgt, x0 + 15, 410), fill=col)

    # candles
    d.rectangle((14, 436, 772, 560), fill=PANEL, outline=LINE)
    d.text((24, 444), "HILL TAPE  ·  NOT A PRICE CHART", font=F_TINY, fill=MUTE)
    base_y = 530
    px = 28
    for i in range(48):
        v = math.sin((t * 1.6) + i * 0.33) * 28 + math.sin(i * 0.9) * 12
        up = v >= 0
        y1 = base_y
        y0 = base_y - abs(v) - 10
        d.rectangle((px, y0, px + 8, y1), fill=COPPER if up else FALL)
        px += 15
    d.text((24, 538), f"{k['name']} walked {58 + int(t) % 17}% of the pump.fun curve", font=F_TINY, fill=MUTE)

    # log
    d.rectangle((790, 436, 1266, 560), fill=PANEL, outline=LINE)
    d.text((806, 444), "HILL LOG", font=F_TINY, fill=MUTE)
    logs = [
        f"SEAT  {books[0]['name']} holds  {money(books[0]['mcap']).strip()}",
        f"CLIMB {books[1]['name']}  {money(books[1]['mcap']).strip()}  +{books[1]['pct']:.1f}%",
        f"LAST  hill print  {money(k['last']).strip()}",
        f"PNL   session  {money(k['pnl']).strip()}",
        f"FALL  ASH dumped  {money(books[7]['mcap']).strip()}",
        f"OPEN  {k['name']} on pump.fun",
    ]
    start = int(t * 1.7) % 4
    for j in range(4):
        line = logs[(start + j) % len(logs)]
        d.text((806, 468 + j * 22), line, font=F_SM, fill=CREAM if j == 0 else MUTE)

    # bottom ticker of dollars
    d.rectangle((0, 572, W, 720), fill=(14, 12, 11))
    tape = "   ·   ".join(
        f"{b['name']} {money(b['mcap']).strip()} {b['pct']:+.1f}%" for b in books
    )
    shift = int((t * 140) % 1800)
    d.text((40 - shift, 596), tape + "   ·   " + tape, font=F_TAPE, fill=COPPER)
    d.text((16, 640), "NO KEYS  ·  NOTHING SENDS  ·  OPEN ON PUMP.FUN  ·  PAPER DESK", font=F_SM, fill=MUTE)
    d.text((1264, 640), "github.com/alexvxonchain/hillwire", font=F_SM, fill=MUTE, anchor="rt")
    d.text((16, 684), f"HILL FLIP  {money(abs(k['last'])).strip()}   SESSION  {money(k['pnl']).strip()}   KING  {k['name']} {money(k['usd']).strip()}", font=F_META, fill=CREAM)

    if 22 <= t < 24.4:
        flash = Image.new("RGB", (W, H), FALL)
        img = Image.blend(img, flash, 0.16 * (math.sin((t - 22) * 9) ** 2))
    return punch(img, t, kick)


def write_bed() -> None:
    sr = 44100
    n = int(sr * SECS)
    mix = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(11)

    def place(sig: np.ndarray, at_s: float, gain: float = 1.0) -> None:
        i = int(at_s * sr)
        if i >= n or i < 0:
            return
        sl = min(len(sig), n - i)
        mix[i : i + sl] += sig[:sl] * gain

    def env_exp(sec: float, speed: float) -> np.ndarray:
        tt = np.arange(int(sec * sr)) / sr
        return tt, np.exp(-tt * speed)

    def kick_body() -> np.ndarray:
        tt, env = env_exp(0.22, 26)
        click = np.exp(-tt * 80) * rng.standard_normal(len(tt)) * 0.25
        body = env * np.sin(2 * np.pi * (130 - 95 * np.minimum(tt / 0.08, 1)) * tt)
        return np.tanh((body + click) * 1.8)

    def eight_oh_eight(start_hz: float) -> np.ndarray:
        tt, env = env_exp(0.95, 3.4)
        slide = np.linspace(start_hz, 36, len(tt))
        sig = env * np.sin(2 * np.pi * np.cumsum(slide) / sr)
        return np.tanh(sig * 2.4)

    def cow(hz: float) -> np.ndarray:
        tt, env = env_exp(0.18, 16)
        metallic = np.sin(2 * np.pi * hz * tt) + 0.55 * np.sin(2 * np.pi * hz * 1.47 * tt)
        metallic += 0.18 * np.sign(np.sin(2 * np.pi * hz * tt))
        return env * metallic

    def clap() -> np.ndarray:
        tt, env = env_exp(0.28, 14)
        noise = rng.standard_normal(len(tt))
        band = np.convolve(noise, np.ones(24) / 24, mode="same")
        tone = np.sin(2 * np.pi * 190 * tt) * 0.2
        return env * (0.7 * band + tone)

    def hat(open_: bool = False) -> np.ndarray:
        tt = np.arange(int((0.09 if open_ else 0.035) * sr)) / sr
        env = np.exp(-tt * (22 if open_ else 70))
        return env * rng.standard_normal(len(tt))

    riff = [523, 0, 415, 0, 466, 0, 523, 0, 415, 0, 349, 0, 415, 466, 523, 0]
    n_beats = int(SECS / BEAT) + 4
    for i in range(n_beats):
        t0 = i * BEAT
        dropped = t0 >= DROP
        place(kick_body(), t0, 1.05 if dropped else 0.35)
        if i % 2 == 0 and dropped:
            hz = 78 if (i // 2) % 4 != 3 else 62
            place(eight_oh_eight(hz), t0, 0.9)
        if i % 2 == 1:
            place(clap(), t0, 0.72 if dropped else 0.2)
        place(hat(False), t0, 0.18 if dropped else 0.1)
        place(hat(False), t0 + BEAT * 0.5, 0.12)
        if i % 4 == 3 and dropped:
            for k in range(4):
                place(hat(False), t0 + BEAT * 0.5 + k * (BEAT / 8), 0.16)
        if i % 4 == 0:
            place(hat(True), t0 + BEAT * 0.75, 0.14 if dropped else 0.06)
        note = riff[i % len(riff)]
        if note:
            place(cow(note), t0, 0.42 if dropped else 0.22)

    t = np.arange(n) / sr
    rumble = 0.05 * np.sin(2 * np.pi * 38 * t)
    rumble *= np.clip((t - DROP) / 0.4, 0, 1)
    mix += rumble
    # sidechain-ish duck after each kick
    phase = (t / BEAT) % 1.0
    duck = 1 - 0.35 * np.exp(-phase * 10)
    mix *= np.where(t >= DROP, duck, 0.75 + 0.25 * duck)
    mix = np.tanh(mix * 1.25)
    peak = np.max(np.abs(mix)) or 1
    mix = mix / peak * 0.95
    stereo = np.column_stack((mix * 0.98, mix))
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(str(WAV), "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main() -> None:
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()
    ASSETS.mkdir(exist_ok=True)
    write_bed()
    n = FPS * SECS
    still_saved = False
    silent = ASSETS / "hillwire_silent.mp4"
    for i in range(n):
        t = i / FPS
        im = frame(t)
        im.save(FRAMES / f"f{i:04d}.png")
        if not still_saved and t >= 9:
            im.save(STILL)
            still_saved = True
        if i % 48 == 0:
            print(f"{i}/{n}")
    subprocess.run(
        [
            "ffmpeg", "-y", "-framerate", str(FPS),
            "-i", str(FRAMES / "f%04d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
            str(silent),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(silent), "-i", str(WAV),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            str(OUT),
        ],
        check=True,
    )
    silent.unlink(missing_ok=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
