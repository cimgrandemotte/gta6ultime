#!/usr/bin/env python3
"""Synthèse audio originale pour le build GTA VI — Ultimate Guide.
Aucun extrait licensed : tout est généré par synthèse (numpy) — pads, nappes,
arpèges dark synthwave, ambiances nature/ville, SFX UI. Sortie : MP3 192 kbps mono.
Usage : python3 tools_synth.py  (depuis la racine gta6-ultimate-guide)
"""
import numpy as np
import lameenc, os, sys, math

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def save_mp3(relpath, x, gain=0.89):
    x = np.tanh(x * 1.1)               # soft limiter
    peak = np.max(np.abs(x)) or 1.0
    x = x / peak * gain
    pcm = (x * 32767).astype(np.int16).tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(192); enc.set_in_sample_rate(SR)
    enc.set_channels(1); enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    path = os.path.join(ROOT, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    print('✓', relpath, f'{len(data)//1024} Ko, {len(x)/SR:.1f}s')

def t_ax(dur):
    return np.linspace(0, dur, int(dur * SR), endpoint=False)

def white(n):  return np.random.default_rng(42).standard_normal(n)

def pink(n):
    w = white(n)
    X = np.fft.rfft(w)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    freqs[0] = freqs[1]
    X = X / np.sqrt(freqs)
    p = np.fft.irfft(X, n)
    return p / (np.max(np.abs(p)) + 1e-9)

def brown(n):
    w = white(n).cumsum()
    w -= w.mean()
    return w / (np.max(np.abs(w)) + 1e-9)

def sine(f, t):    return np.sin(2 * np.pi * f * t)
def square(f, t):  return np.sign(np.sin(2 * np.pi * f * t))
def tri(f, t):     return 2 / np.pi * np.arcsin(np.sin(2 * np.pi * f * t))

def adsr(n, a, d, s_level, r, sus_frac=0.6):
    e = np.full(n, s_level)
    ia, idd, ir = int(a * SR), int(d * SR), int(r * SR)
    e[:ia] = np.linspace(0, 1, ia, endpoint=False)
    e[ia:ia + idd] = np.linspace(1, s_level, idd, endpoint=False)
    e[-ir:] *= np.linspace(1, 0, ir, endpoint=True)
    return e

def note(freq, dur, kind='saw', a=0.01, d=0.15, s=0.7, r=0.25, det=0.004):
    t = t_ax(dur); n = len(t)
    if kind == 'saw':
        sig = 0.6 * sine(freq, t) + 0.3 * sine(freq * 2.003, t) + 0.15 * sine(freq * 3.005, t)
        sig += 0.4 * sine(freq * (1 + det), t) + 0.2 * sine(freq * 2 * (1 - det), t)
    elif kind == 'sub':
        sig = 0.9 * sine(freq, t) + 0.3 * sine(freq * 2, t)
    elif kind == 'tri':
        sig = tri(freq, t)
    elif kind == 'bell':
        sig = sine(freq, t) + 0.5 * sine(freq * 2.01, t) + 0.28 * sine(freq * 2.74, t) + 0.12 * sine(freq * 3.76, t)
    else:
        sig = sine(freq, t)
    return sig * adsr(n, a, d, s, r)

def add_at(buf, sig, at_sec):
    i = int(at_sec * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]

# ── 1) Homepage ambiance — Vice City night (24s) ─────────────────────────────
def homepage_ambiance():
    dur = 24; t = t_ax(dur); n = len(t)
    surf = pink(n) * (0.35 + 0.65 * np.abs(np.sin(2 * np.pi * t / 6.3))) * 0.5
    hum  = (0.10 * sine(55, t) + 0.05 * sine(110, t) + 0.02 * sine(220, t)) * (0.8 + 0.2 * np.sin(2 * np.pi * t / 11))
    chord = [110.0, 164.81, 246.94, 293.66]   # A2 E3 B3 D4 — pad mineur coloré
    pad = np.zeros(n)
    for f in chord:
        pad += sine(f, t) * (0.75 + 0.25 * np.sin(2 * np.pi * t / 8 + f)) + 0.4 * sine(f * 1.004, t) + 0.2 * sine(f * 2.001, t)
    pad *= 0.16 * np.minimum(1, t / 2.5) * np.minimum(1, (dur - t) / 2.5)
    shimmer = sum(sine(f * 4, t + 0.1 * k) * 0.012 for k, f in enumerate(chord))
    x = surf + hum + pad + shimmer
    x *= np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.5)
    save_mp3('assets/audio/ambiances/homepage_ambiance_vicecity_night_01.mp3', x)

# ── 2/3) UI blips ────────────────────────────────────────────────────────────
def ui_hover():
    dur = 0.18; t = t_ax(dur)
    f = 1320 * np.exp(np.log(1760 / 1320) * t / dur)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    x += 0.3 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * np.exp(-t * 18)
    save_mp3('assets/audio/ui/homepage_ui_hover_01.mp3', x * 0.7)

def ui_click():
    dur = 0.09; t = t_ax(dur)
    x = square(880, t) * np.exp(-t * 45) * 0.8
    x += white(len(t)) * np.exp(-t * 220) * 0.9 * (t < 0.012)
    save_mp3('assets/audio/ui/homepage_ui_click_01.mp3', x * 0.7)

# ── 4) Page transition whoosh (1.4s) ─────────────────────────────────────────
def ui_transition():
    dur = 1.4; t = t_ax(dur); n = len(t)
    env = np.sin(np.pi * t / dur) ** 1.6
    sweep = 300 * (4000 / 300) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(sweep) / SR
    tonal = np.sin(ph) * 0.25
    noise = white(n)
    # one-pole lowpass, cutoff sweeping up then down
    fc = np.where(t < dur / 2, sweep, 4000 * (300 / 4000) ** ((t - dur / 2) / (dur / 2)))
    alpha = np.clip(fc / (fc + SR / (2 * np.pi)), 0, 1)
    lp = np.empty(n); acc = 0.0
    for i in range(n):
        acc += alpha[i] * (noise[i] - acc); lp[i] = acc
    lp /= np.max(np.abs(lp)) + 1e-9
    x = (lp * 0.8 + tonal) * env
    save_mp3('assets/audio/ui/homepage_ui_transition_01.mp3', x)

# ── helper: pattern sequencer ────────────────────────────────────────────────
def seq(events, dur):
    buf = np.zeros(int(dur * SR))
    for at, freq, length, kind, vol in events:
        sig = note(freq, length, kind=kind) * vol
        add_at(buf, sig, at)
    return buf

def kick(buf, at):
    dur = 0.32; t = t_ax(dur)
    f = 120 * np.exp(-t * 9) + 43
    k = sine(1, t) * 0  # placeholder replaced below
    k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    add_at(buf, k * 0.95, at)

def hat(buf, at, vol=0.22):
    t = t_ax(0.05)
    h = white(len(t)) * np.exp(-t * 90)
    add_at(buf, h * vol, at)

# ── 5) Jason theme — dark synthwave (18s, 92 bpm, Am) ───────────────────────
def jason_theme():
    bpm = 92; beat = 60 / bpm; e8 = beat / 2; dur = 8 * 4 * beat + 1.6
    Am = [110.00, 130.81, 164.81]   # A2 C3 E3
    F  = [87.31, 130.81, 174.61]    # F2 C3 F3
    G  = [98.00, 123.47, 146.83]    # G2 B2 D3
    bars = [Am, Am, F, G, Am, Am, F, G]
    x = np.zeros(int(dur * SR))
    for bi, ch in enumerate(bars):
        t0 = bi * 4 * beat
        for b in range(4):
            kick(x, t0 + b * beat)
            hat(x, t0 + b * beat + e8, 0.18)
        add_at(x, note(ch[0] / 2, 4 * beat, kind='sub', a=0.02, d=0.2, s=0.9, r=0.2) * 0.85, t0)
        arp = [ch[0] * 2, ch[1] * 2, ch[2] * 2, ch[1] * 2]
        for k in range(8):
            add_at(x, note(arp[k % 4], e8 * 0.92, kind='saw', a=0.005, d=0.08, s=0.5, r=0.1) * 0.34, t0 + k * e8)
    lead = [440.0, 523.25, 659.26, 587.33, 523.25, 440.0, 392.0, 329.63]
    for i, f in enumerate(lead):
        seg_start = i * e8 * 2
        add_at(x, note(f, e8 * 1.7, kind='saw', a=0.02, d=0.2, s=0.75, r=0.3) * 0.30, seg_start)
    # simple echo
    echo = np.zeros_like(x); d = int(e8 * 2 * SR)
    echo[d:] = x[:-d] * 0.32
    x = x + echo
    save_mp3('assets/audio/jingles/characters_jason_theme_01.mp3', x * 0.9)

# ── 6) Lucia theme — motif déterminé (18s, 100 bpm, Dm) ─────────────────────
def lucia_theme():
    bpm = 100; beat = 60 / bpm; e8 = beat / 2; dur = 8 * 4 * beat + 1.6
    Dm = [73.42, 87.31, 110.0]
    Bb = [58.27, 87.31, 116.54]
    F  = [87.31, 110.0, 130.81]
    C  = [65.41, 98.0, 130.81]
    bars = [Dm, Bb, F, C, Dm, Bb, F, C]
    x = np.zeros(int(dur * SR))
    for bi, ch in enumerate(bars):
        t0 = bi * 4 * beat
        for b in range(4):
            kick(x, t0 + b * beat)
            for s in range(4):
                hat(x, t0 + b * beat + s * (beat / 4), 0.10)
        pad = sum(note(f * 2, 4 * beat, kind='saw', a=0.4, d=0.4, s=0.85, r=0.6) for f in ch)
        add_at(x, pad * 0.16, t0)
    mel = [293.66, 349.23, 440.0, 349.23, 293.66, 261.63, 233.08, 196.0,
           220.0, 261.63, 293.66, 349.23, 293.66, 349.23, 440.0, 523.25]
    for i, f in enumerate(mel):
        vib = note(f, e8 * 1.8, kind='tri', a=0.03, d=0.2, s=0.8, r=0.35)
        t = t_ax(len(vib) / SR)
        vib *= (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t))
        add_at(x, vib * 0.42, i * e8 * 2)
    save_mp3('assets/audio/jingles/characters_lucia_theme_01.mp3', x * 0.9)

# ── 7) Map ambiance — nature Floride (22s) ───────────────────────────────────
def map_ambiance():
    dur = 22; t = t_ax(dur); n = len(t)
    wind = pink(n) * (0.45 + 0.4 * np.sin(2 * np.pi * t / 9 + 1.2) ** 2) * 0.55
    water = brown(n) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 4.7) ** 2) * 0.25
    x = wind + water
    rng = np.random.default_rng(7)
    for _ in range(15):
        at = rng.uniform(0.5, dur - 1.0)
        f0 = rng.uniform(1700, 3100)
        cl = rng.uniform(0.14, 0.32)
        tt = t_ax(cl)
        f = f0 * (1 + 0.35 * np.sin(2 * np.pi * 9 * tt + rng.uniform(0, 6)))
        chirp = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / cl) ** 2
        add_at(x, chirp * rng.uniform(0.10, 0.2), at)
    far = np.sin(2 * np.pi * 38 * t) * 0.05 * (np.sin(2 * np.pi * t / 13) ** 6)
    x += far
    x *= np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2)
    save_mp3('assets/audio/ambiances/map_leonida_ambiance_01.mp3', x)

# ── 8) Weapons equip — métallique (0.7s) ────────────────────────────────────
def weapons_equip():
    x = np.zeros(int(0.72 * SR))
    def clack(at, base):
        t = t_ax(0.16)
        hit = white(len(t)) * np.exp(-t * 60) * 0.8
        hit = np.fft.irfft(np.fft.rfft(hit) * np.where((np.fft.rfftfreq(len(t), 1 / SR) > 900) & (np.fft.rfftfreq(len(t), 1 / SR) < 3400), 1, 0.05), len(t))
        metal = (sine(base, t) + 0.6 * sine(base * 2.76, t) + 0.3 * sine(base * 5.4, t)) * np.exp(-t * 22)
        add_at(x, hit * 0.5 + metal * 0.55, at)
    clack(0.0, 1150)
    clack(0.30, 830)
    save_mp3('assets/audio/ui/weapons_equip_sound_01.mp3', x)

# ── 9) V8 engine start (3.5s) ───────────────────────────────────────────────
def engine_v8():
    dur = 3.5; t = t_ax(dur); n = len(t)
    base = 50 + 42 * np.exp(-((t - 2.6) / 0.5) ** 2) - 6 * np.minimum(t / dur, 1)
    ph = 2 * np.pi * np.cumsum(base) / SR
    sig = (np.sign(np.sin(ph)) * 0.55 + sine(1, t) * 0 + 0.35 * np.sin(2 * ph) + 0.22 * np.sin(3 * ph) + 0.15 * np.sin(4.02 * ph))
    lump = 0.72 + 0.28 * np.sin(2 * np.pi * base * 4.5 * t) ** 4
    noise = white(n) * 0.06
    x = sig * lump * 0.8 + noise
    x *= np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.4)
    save_mp3('assets/audio/ambiances/vehicles_engine_v8_01.mp3', x)

# ── 10) Quiz correct — carillon victoire (0.95s) ────────────────────────────
def quiz_correct():
    x = np.zeros(int(0.95 * SR))
    for i, f in enumerate([659.25, 783.99, 987.77, 1318.51]):
        add_at(x, note(f, 0.62, kind='bell', a=0.005, d=0.25, s=0.35, r=0.35) * (0.5 + 0.14 * i), i * 0.12)
    save_mp3('assets/audio/jingles/quiz_correct_answer_01.mp3', x)

HOMEPAGE_AMBIANCE = homepage_ambiance()
ui_hover(); ui_click(); ui_transition()
jason_theme(); lucia_theme(); map_ambiance()
weapons_equip(); engine_v8(); quiz_correct()
print('Tous les audios générés.')
