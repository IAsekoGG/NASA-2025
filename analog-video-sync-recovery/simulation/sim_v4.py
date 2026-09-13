#!/usr/bin/env python3
"""
Поведінкова симуляція прототипу v4-мін:
  CVBS (PAL) + шум/пропадання → LM1881 (ФНЧ, clamp, поріг 70 мВ) → інвертор →
  CD4046 PC2 (частотно-фазовий детектор) + lag-lead фільтр + VCO (лінійний, обмежений діапазон) →
  формувач 4.7 мкс → шунт-ключ на V_SYNC → вихід.
Оцінює: похибку періоду вихідних рядків, фазову похибку, «проксі синього екрана» (ADV7180-подібний лічильник).

Запуск:  python3 sim_v4.py            (усі сценарії)
         python3 sim_v4.py B_narrow   (один сценарій)
Результати: results/<сценарій>.png та results/summary.md
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- параметри сигналу PAL ----------------
FS = 10e6            # частота дискретизації, Гц (dt = 0.1 мкс)
DT = 1.0 / FS
H = 64.0e-6          # номінальний період рядка
SYNC_W = 4.7e-6
BURST_START, BURST_END = 5.6e-6, 7.85e-6
ACTIVE_START = 10.4e-6
LINES_PER_FIELD = 312.5

def gen_cvbs(n_lines, line_period=H, apl=0.4, seed=0):
    """Повертає (video[V], sync_starts[s]) — спрощений PAL з VBI (eq/broad), burst і «картинкою»."""
    rng = np.random.default_rng(seed)
    n = int(round(n_lines * line_period * FS))
    v = np.zeros(n, dtype=np.float32)
    t = np.arange(int(round(line_period * FS))) * DT
    # звичайний рядок
    line = np.zeros_like(t, dtype=np.float32)
    line[t < SYNC_W] = -0.3
    b = (t >= BURST_START) & (t < BURST_END)
    line[b] = 0.15 * np.sin(2 * np.pi * 4.43361875e6 * t[b])
    act = t >= ACTIVE_START
    # «картинка»: повільна хвиля + смуги (є контент від 0 до 0.7 В)
    line[act] = 0.05 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t[act] / (line_period - ACTIVE_START)))**1.5 * apl / 0.4
    line = np.clip(line, -0.3, 0.7)
    # VBI: eq-імпульси (2.35 мкс кожні 32 мкс) та broad (27.3 мкс кожні 32 мкс)
    eq = np.zeros_like(t, dtype=np.float32); eq[(t % 32e-6) < 2.35e-6] = -0.3
    broad = np.zeros_like(t, dtype=np.float32); broad[(t % 32e-6) < 27.3e-6] = -0.3
    sync_starts = []
    ln = len(t)
    for k in range(n_lines):
        pos = k % 625
        fpos = pos % 312   # позиція в полі (спрощено, без півлінійного зсуву)
        if fpos < 2 or (5 <= fpos < 7):
            seg = eq
        elif 2 <= fpos < 5:
            seg = broad
        else:
            seg = line
        s = k * ln
        v[s:s + ln] = seg[: min(ln, n - s)]
        sync_starts.append(k * line_period)
    return v, np.array(sync_starts)

# ---------------- LM1881 (поведінково) ----------------
def lm1881(vin, thresh=0.07, lpf_fc=500e3, clamp_attack_tau=2e-6, clamp_release_tau=5e-3, min_pw=0.3e-6):
    """Вхідний ФНЧ → clamp по найнижчому рівню (швидка атака, повільний відпуск) → компаратор на +70 мВ.
    Повертає масив csync (1 = sync активний) та індекси спадних фронтів (початки sync)."""
    a = np.exp(-2 * np.pi * lpf_fc * DT)
    y = np.empty_like(vin)
    acc = 0.0
    # однополюсний ФНЧ
    from itertools import accumulate
    y = np.asarray(list(accumulate(vin, lambda p, x: a * p + (1 - a) * x)), dtype=np.float32)
    # clamp: рівень tip, що слідує за мінімумом
    tip = np.empty_like(y)
    lvl = float(y[0]); ka = DT / clamp_attack_tau; kr = DT / clamp_release_tau
    for i in range(len(y)):
        s = y[i]
        if s < lvl: lvl += (s - lvl) * ka
        else:       lvl += (s - lvl) * kr
        tip[i] = lvl
    cs = (y < tip + thresh)
    # мінімальна ширина імпульсу (фільтр коротких викидів)
    minw = int(min_pw * FS)
    d = np.diff(cs.astype(np.int8))
    starts = np.where(d == 1)[0] + 1
    ends = np.where(d == -1)[0] + 1
    if cs[0]: starts = np.r_[0, starts]
    if cs[-1]: ends = np.r_[ends, len(cs)]
    keep = (ends - starts) >= minw
    return cs, starts[keep], ends[keep]

# ---------------- CD4046: PC2 + фільтр + VCO, формувач, ключ ----------------
def pll_run(sig_edges_t, t_end, fmin, fmax, R3, R4, C, VDD=5.0, v9_init=None, phase_init=None, inhibit=50e-6):
    """Подієво-крокова симуляція PC2 (PFD) з lag-lead фільтром і VCO. Повертає часи фронтів VCO та V9(t)."""
    dt = 0.1e-6
    n = int(t_end / dt)
    sig = np.zeros(n, dtype=bool)
    idx = (sig_edges_t / dt).astype(int); idx = idx[(idx >= 0) & (idx < n)]
    sig[idx] = True
    if v9_init is None:
        v9_init = VDD * (1 / H - fmin) / (fmax - fmin)   # стартуємо з правильної напруги (після початкового захоплення)
        v9_init = float(np.clip(v9_init, 0, VDD))
    vc = v9_init
    up = down = False
    f0 = fmin + (fmax - fmin) * vc / VDD
    # старт у захопленому стані: перший фронт VCO збігається з першим фронтом SIG (окремий сценарій G перевіряє захоплення)
    phase = (1.0 - f0 * float(sig_edges_t[0])) % 1.0 if (len(sig_edges_t) and phase_init is None) else (phase_init or 0.0)
    vco_edges = []
    nl = (n + 99) // 100
    v9_log = np.zeros(nl, dtype=np.float32)
    f_log = np.zeros(nl, dtype=np.float32)
    last_acc = -1.0
    inh_steps = int(inhibit / dt)
    for i in range(n):
        # PFD; вікно: після прийнятого фронту решта фронтів блокується на inhibit (мертвий час Q5)
        if sig[i] and (i - last_acc) > inh_steps:
            up = True; last_acc = i
        # напруга на pin 9 = напруга конденсатора + падіння на R4 під час накачки (нуль lag-lead фільтра)
        if up:     v9 = vc + (VDD - vc) * R4 / (R3 + R4)
        elif down: v9 = vc + (0.0 - vc) * R4 / (R3 + R4)
        else:      v9 = vc
        f = fmin + (fmax - fmin) * min(max(v9 / VDD, 0.0), 1.0)
        phase += f * dt
        comp = False
        if phase >= 1.0:
            phase -= 1.0; comp = True
            vco_edges.append(i * dt)
        if comp: down = True
        if up and down: up = down = False
        # фільтр
        if up:   vc += (VDD - vc) / (R3 + R4) * dt / C
        elif down: vc += (0.0 - vc) / (R3 + R4) * dt / C
        if i % 100 == 0:
            v9_log[i // 100] = v9; f_log[i // 100] = f
    return np.array(vco_edges), v9_log, f_log, dt * 100

def relock_time(vco_edges, true_starts, line_period, t_evt):
    j=0; good=0
    for e in vco_edges:
        if e < t_evt: continue
        while j + 1 < len(true_starts) and true_starts[j + 1] <= e + line_period / 2: j += 1
        d = abs(e - true_starts[j] - 0.65e-6)
        good = good + 1 if d < 1e-6 else 0
        if good >= 20: return (e - t_evt) * 1e3
    return None

def analyze(vco_edges, true_starts, line_period):
    """Метрики за вихідними рядками (початки вставленого sync = фронти VCO)."""
    per = np.diff(vco_edges)
    err_pct = (per - line_period) / line_period * 100
    bad = np.abs(err_pct) > 5.0
    # проксі «синій екран»: втрата lock, якщо ≥32 підряд поганих рядків (ADV7180-подібно)
    run = 0; maxrun = 0; blue = 0
    for b in bad:
        run = run + 1 if b else 0
        maxrun = max(maxrun, run)
        if run == 32: blue += 1
    # фазова похибка відносно справжніх sync (де вони є)
    ph = []
    j = 0
    for e in vco_edges:
        if e > true_starts[-1] + line_period / 2: break
        while j + 1 < len(true_starts) and true_starts[j + 1] <= e + line_period / 2: j += 1
        d = e - true_starts[j]
        if abs(d) < line_period / 2: ph.append(d)
    ph = np.array(ph) * 1e6
    return dict(lines=len(per), err_rms_pct=float(np.sqrt(np.mean(err_pct**2))), err_max_pct=float(np.max(np.abs(err_pct))),
                bad_lines=int(bad.sum()), max_bad_run=int(maxrun), blue_events=int(blue),
                phase_rms_us=float(np.sqrt(np.mean(ph**2))) if len(ph) else None,
                phase_max_us=float(np.max(np.abs(ph))) if len(ph) else None), err_pct, ph

# ---------------- сценарії ----------------
def scenario(name, dur=0.30, line_period=H, snr_profile=None, dropout=None, silence=None,
             vco=(15.3e3, 16.3e3), filt=(22e3, 10e3, 1e-6), seed=1, phase_init=None, v9_init=None, inhibit=50e-6):
    rng = np.random.default_rng(seed)
    n_lines = int(dur / line_period)
    v, starts = gen_cvbs(n_lines, line_period)
    t = np.arange(len(v)) * DT
    # амплітуда сигналу та шум за часом
    amp = np.ones_like(v)
    sigma = np.zeros_like(v)
    if snr_profile is None: snr_profile = lambda tt: 35.0
    snr = np.array([snr_profile(tt) for tt in t[::1000]])
    sigma_c = 1.0 / (10 ** (snr / 20))           # σ шуму відносно 1 Vpp
    sigma = np.repeat(sigma_c, 1000)[: len(v)].astype(np.float32)
    if dropout:
        for (a, b) in dropout:
            m = (t >= a) & (t < b); amp[m] = 0.0; sigma[m] = 0.30   # «сніг» приймача ≈300 мВ σ
    if silence:
        for (a, b) in silence:
            m = (t >= a) & (t < b); amp[m] = 0.0; sigma[m] = 0.0
    noise = rng.normal(0, 1, len(v)).astype(np.float32) * sigma
    # шум приймача обмежений смугою ~5 МГц — грубо ФНЧ
    vin = v * amp + noise
    cs, s_idx, e_idx = lm1881(vin)
    sig_edges_t = s_idx * DT + 0.15e-6        # затримка LM1881 + інвертор
    vco_edges, v9, f_log, dtl = pll_run(sig_edges_t, dur, vco[0], vco[1], *filt, v9_init=v9_init, phase_init=phase_init, inhibit=inhibit)
    m, err, ph = analyze(vco_edges, starts, line_period)
    m["false_edges_per_line"] = float(len(s_idx) / n_lines)
    ev = (dropout or silence or [(None,None)])[-1][1]
    m["relock_ms"] = relock_time(vco_edges, starts, line_period, ev) if ev else None
    m["vco_f_min_kHz"], m["vco_f_max_kHz"] = float(f_log.min() / 1e3), float(f_log.max() / 1e3)
    # графік
    fig, ax = plt.subplots(4, 1, figsize=(11, 9.5), sharex=True)
    tl = np.arange(len(f_log)) * dtl * 1e3
    ax[0].plot(tl, f_log / 1e3, lw=1); ax[0].axhline(1 / H / 1e3, color="k", ls="--", lw=.7)
    ax[0].axhspan(1 / H / 1e3 * 0.95, 1 / H / 1e3 * 1.05, color="g", alpha=.08)
    ax[0].set_ylabel("VCO, кГц"); ax[0].set_title(f"{name}: частота VCO (зелена смуга = ±5 %)")
    te = vco_edges[1:] * 1e3
    ax[1].plot(te, err, lw=.6); ax[1].axhspan(-5, 5, color="g", alpha=.08); ax[1].set_ylabel("похибка періоду, %")
    ax[1].set_ylim(-15, 15)
    ax[2].plot(vco_edges[:len(ph)] * 1e3, ph, lw=.6); ax[2].axhspan(-1, 2.3, color="g", alpha=.08); ax[2].set_ylabel("фаза vs справжній sync, мкс"); ax[2].set_ylim(-33, 33)
    tt = t[::100] * 1e3
    ax[3].plot(tt, sigma[::100] * 1e3, lw=.8, label="σ шуму, мВ"); ax[3].plot(tt, amp[::100] * 300, lw=.8, label="сигнал (300=є, 0=нема)")
    ax[3].legend(loc="upper right"); ax[3].set_ylabel("вхід"); ax[3].set_xlabel("час, мс")
    fig.tight_layout(); os.makedirs("results", exist_ok=True)
    fig.savefig(f"results/{name}.png", dpi=110); plt.close(fig)
    return m

SCEN = {
  # A: чистий сигнал — базова поведінка, «гачок» від VBI
  "A_clean":          dict(),
  # A0: те саме БЕЗ мертвого часу (чистий PC2 як у v2) — VBI-імпульси зривають PLL
  "A0_clean_nogate":  dict(inhibit=0.0),
  "A0_clean_nogate_fastloop": dict(inhibit=0.0, filt=(10e3, 4.7e3, 1e-6)),
  # G: захоплення з довільної фази та VCO на краю діапазону (після ввімкнення)
  "G_acquire":        dict(dur=1.5, phase_init=0.5, v9_init=0.5),
  # B: пропадання 5 кадрів (100 мс) зі снігом; вузький VCO-діапазон (наш вибір)
  "B_dropout_narrow": dict(dropout=[(0.10, 0.20)]),
  # B2: те саме, але широкий діапазон VCO як у v2 (10–20 кГц) — показує, чому діапазон треба обмежити
  "B_dropout_wide":   dict(dropout=[(0.10, 0.20)], vco=(10e3, 20e3)),
  # B3: пропадання без мертвого часу (для порівняння)
  "B_dropout_nogate": dict(dropout=[(0.10, 0.20)], inhibit=0.0),
  # C: плавна деградація SNR 35 → 3 дБ
  "C_snr_ramp":       dict(snr_profile=lambda tt: 35 - 32 * min(tt / 0.30, 1.0)),
  # D: камера з періодом 64.3 мкс (+0.5 %) і 65.0 мкс (+1.6 %)
  "D_cam_64p3":       dict(line_period=64.3e-6),
  "D_cam_65p0":       dict(line_period=65.0e-6),
  # E: приймач мутить у тишу (без шуму) на 100 мс — PC2 у tri-state, VCO тримає
  "E_silence":        dict(silence=[(0.10, 0.20)]),
  # F: короткі пропадання по 2 кадри тричі
  "F_bursts":         dict(dropout=[(0.08, 0.12), (0.16, 0.20), (0.24, 0.28)]),
}

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    names = sys.argv[1:] or list(SCEN)
    rows = []
    for nm in names:
        m = scenario(nm, **SCEN[nm])
        rows.append((nm, m)); print(nm, json.dumps(m, ensure_ascii=False))
    with open("results/summary.md", "w") as f:
        f.write("| сценарій | рядків | хибних фронтів/рядок | VCO min–max, кГц | похибка періоду RMS/max, % | поганих рядків (>5 %) | макс. серія | «синій екран» (≥32 підряд) | фаза RMS/max, мкс | повторний lock, мс |\n|---|---|---|---|---|---|---|---|---|---|\n")
        for nm, m in rows:
            f.write(f"| {nm} | {m['lines']} | {m['false_edges_per_line']:.2f} | {m['vco_f_min_kHz']:.2f}–{m['vco_f_max_kHz']:.2f} | {m['err_rms_pct']:.2f} / {m['err_max_pct']:.2f} | {m['bad_lines']} | {m['max_bad_run']} | {m['blue_events']} | {m['phase_rms_us'] if m['phase_rms_us'] is None else round(m['phase_rms_us'],2)} / {m['phase_max_us'] if m['phase_max_us'] is None else round(m['phase_max_us'],2)} | {'' if m.get('relock_ms') is None else round(m['relock_ms'],0)} |\n")
    print("written results/summary.md")
