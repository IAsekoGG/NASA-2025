#!/usr/bin/env python3
"""
Поведінкова симуляція Системи 2.0:
  CVBS (PAL, повна структура VBI з півлінійним зсувом) + шум/пропадання
  → keyed clamp (строб на back porch, від трекера) → ФНЧ 300 кГц (тільки в гілці компаратора)
  → компаратор на V_BLANK − 150 мВ + цифровий дебаунс 0.5 мкс (як вхідний фільтр таймера STM32)
  → трекер входу (IT): кандидат → 16 влучень = TRACKING; вікно ±1.5 мкс; PI-оцінка періоду; 8 промахів → NONE
  → вихідна шкала (OT): завжди синтетичний CSYNC від кварцу; фаза підтягується до IT
     зі слew ≤1 мкс/рядок; період = оцінка IT (COAST тримає останній); лічильник рядків 0…624,
     кадр за broad-імпульсами.
Метрики ті самі, що у sim_v4/sim_v6 (похибка періоду, «синій екран», фаза vs справжній sync),
плюс стан трекера, час захоплення, помилка clamp, хибні імпульси.

Запуск: python3 sim_v20.py            (усі сценарії)
        python3 sim_v20.py A_clean    (один)
Результати: results/S2_<сценарій>.png/.npz, results/S2_summary.md
"""
import sys, os, json
from itertools import accumulate
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 10e6; DT = 1.0 / FS
H = 64.0e-6
SYNC_W, EQ_W, BROAD_W = 4.7e-6, 2.35e-6, 27.3e-6
BURST_START, BURST_END = 5.6e-6, 7.85e-6
ACTIVE_START = 10.4e-6
V_BLANK, V_THR, V_SYNC = 0.60, 0.45, 0.30      # вольти на вузлі (дільник 3.3 В)

# ---------------- генератор PAL з повним VBI ----------------
def gen_cvbs(n_lines, line_period=H, apl=0.4, seed=0, content="bands"):
    """Повертає (video[V відносно blanking], sync_starts[s]) — PAL: 625 рядків, поле 1 = 0…312.5, поле 2 = 312.5…625.
    VBI: 2.5 рядки pre-eq, 2.5 broad, 2.5 post-eq (з півлінійним зсувом у полі 2), потім чорні рядки до 23-го."""
    L = int(round(line_period * FS))
    t = np.arange(L) * DT
    def hsync_line(active):
        s = np.zeros(L, np.float32); s[t < SYNC_W] = -0.3
        b = (t >= BURST_START) & (t < BURST_END); s[b] = 0.15 * np.sin(2 * np.pi * 4.43361875e6 * t[b])
        if active:
            act = t >= ACTIVE_START
            x = (t[act] - ACTIVE_START) / (line_period - ACTIVE_START)
            if content == "bands":
                s[act] = 0.05 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * x))**1.5 * apl / 0.4
            elif content == "darkbar":   # яскраве поле з чорною смугою 4.7 мкс (рівень blanking) — пастка для сепаратора
                s[act] = 0.55
                bar = act & (t >= 30e-6) & (t < 30e-6 + SYNC_W); s[bar] = 0.0
            elif content == "flat":
                s[act] = 0.3
        return np.clip(s, -0.3, 0.7)
    act_line, blank_line = hsync_line(True), hsync_line(False)
    half = L // 2
    n = n_lines * L
    v = np.zeros(n + L, np.float32)
    starts = np.arange(n_lines) * L * DT        # справжні початки рядків (за фактичною дискретизацією)
    for k in range(n_lines):
        pos = k % 625
        fpos = pos if pos < 313 else pos - 313
        seg = act_line if 23 <= fpos <= 309 else blank_line
        v[k * L:(k + 1) * L] = seg
    # вертикальні імпульси: 15 імпульсів по 32 мкс, починаючи з 0 (поле 1) і 312.5 (поле 2) рядка
    pat = np.zeros(15 * half, np.float32)
    tp = np.arange(15 * half) * DT
    for i in range(15):
        w = BROAD_W if 5 <= i < 10 else EQ_W
        pat[(tp >= i * half * DT) & (tp < i * half * DT + w)] = -0.3
    for k in range(n_lines):
        pos = k % 625
        if pos == 0:  s = k * L
        elif pos == 313: s = k * L - half       # 312.5
        else: continue
        if s < 0: continue
        e = min(s + len(pat), n + L); v[s:e] = pat[: e - s]
    return v[:n], starts

def lpf1(x, fc):
    a = np.exp(-2 * np.pi * fc * DT)
    return np.asarray(list(accumulate(x, lambda p, s: a * p + (1 - a) * s)), dtype=np.float32)

# ---------------- Система 2.0: аналоговий фронт + трекер + синтез ----------------
def s2_run(vin, t_end, line_period_true, dc_init=-0.5, W=1.5e-6, hits_lock=16, miss_unlock=8,
           clamp_tau=18e-6, strobe=(8.2e-6, 9.4e-6), comp_fc=300e3, min_pw=0.5e-6, q_min=0.35, dc_tol=0.25,
           a_ph=0.15, b_T=0.01, slew=1.0e-6, k_fine=0.5, T_init=H, ot_phase_init=0.0, T_coast=2.0, delay_comp=0.6e-6):
    """vin — сигнал на вході (В, blanking = 0 без зсуву). Повертає словник логів."""
    n = len(vin); t_end = min(t_end, n * DT)
    y = lpf1(vin, comp_fc)          # гілка компаратора (ФНЧ не в тракті відео)
    minw = int(min_pw * FS)
    g_clamp = 1 - np.exp(-(strobe[1] - strobe[0]) / clamp_tau)   # частка корекції за один строб
    dc = dc_init                    # напруга на конденсаторі: вузол = vin + dc; ціль: blanking → V_BLANK
    thr = V_THR
    # --- стан трекера входу (IT)
    it_state = 0                    # 0 NONE, 1 CANDIDATE, 2 TRACKING
    it_phi = None; it_T = T_init; it_hits = 0; it_miss = 0
    broad_seen = 0; v_in_ref = None; v_in_L = 0; n_edges = 0; v_locks = 0; ever_locked_t = -1.0; v_pending = None; T_good = T_init; seed_toggle = True; lock_lines = 0
    # --- вихідна шкала (OT)
    ot_t = ot_phase_init; ot_T = T_init; L = 0; ot_vlocked = False
    # --- логи по вихідних рядках
    out_starts = []; out_kind = []; log_state = []; log_dc = []; log_T = []; log_it_phi = []; log_pulses = []
    v_resync = 0; first_lock = None
    prev_cs = False; pulse_start = None; pulse_end = None; tip_est = V_SYNC; q_width = 1.0; bad_dc_lines = 0
    pulses_pending = []             # (start, end) виявлені імпульси, ще не оброблені трекером
    chunk_from = 0
    while ot_t < t_end:
        # ---- 1. вихідний рядок L з початком ot_t (синтез)
        pos = L % 625; fpos = pos if pos < 313 else pos - 313
        kind = "V" if fpos < 8 else "H"
        st_eff = 2 if (it_state == 2 and q_width >= 0.6) else min(it_state, 1)
        st_log = st_eff if (st_eff == 2 or ever_locked_t < 0 or ot_t - ever_locked_t > T_coast) else 3   # 3 = COAST
        out_starts.append(ot_t); out_kind.append(kind); log_state.append(st_log); log_dc.append(dc); log_T.append(ot_T)
        log_it_phi.append(np.nan if it_phi is None else it_phi)
        # ---- 2. обробка вхідного відрізка [попередній край, ot_t + T/2): усе, що передує наступному рядку
        chunk_to = min(int((ot_t + 0.5 * ot_T) / DT), n)
        if chunk_to > chunk_from:
            seg = y[chunk_from:chunk_to] + dc
            cs = seg < thr
            d = np.diff(np.r_[prev_cs, cs].astype(np.int8))
            f_idx = set((np.where(d == 1)[0] + chunk_from).tolist()); r_idx = (np.where(d == -1)[0] + chunk_from).tolist()
            # симетричний дебаунс: провали (high) коротші за min_pw зливаються з імпульсом, імпульси коротші за min_pw відкидаються
            for i in sorted(list(f_idx) + r_idx):
                if i in f_idx:                                   # спад: початок (або продовження) імпульсу
                    if pulse_end is not None and (i - pulse_end) < minw:
                        pulse_end = None                         # короткий провал — злити
                    else:
                        if pulse_start is not None and pulse_end is not None and (pulse_end - pulse_start) >= minw:
                            pulses_pending.append((pulse_start * DT, pulse_end * DT))
                        pulse_start = i; pulse_end = None
                else:                                            # фронт вгору: тимчасовий кінець
                    if pulse_start is not None: pulse_end = i
            if pulse_start is not None and pulse_end is not None and (chunk_to - pulse_end) >= minw:
                if (pulse_end - pulse_start) >= minw: pulses_pending.append((pulse_start * DT, pulse_end * DT))
                pulse_start = None; pulse_end = None
            prev_cs = bool(cs[-1])
            # оцінка вершини sync за АЦП (гілка ФНЧ): медіана найнижчих 7 % відліків ≈ 3.6-й процентиль
            tip_est = float(np.percentile(y[chunk_from:chunk_to], 3.6)) + dc
            n_edges += len(f_idx)
            # clamp
            if it_state == 2:
                # LOCKED: строб на back porch від фази трекера (найближчий очікуваний імпульс усередині відрізка)
                ph = it_phi
                while ph >= chunk_from * DT + it_T: ph -= it_T
                while ph < chunk_from * DT: ph += it_T
                sa, sb = int((ph + strobe[0]) / DT), int((ph + strobe[1]) / DT)
                if chunk_from <= sa and sb <= chunk_to:
                    m = float(np.mean(vin[sa:sb])) + dc
                    dc += (V_BLANK - m) * g_clamp
                # перевірка правдоподібності lock: вершина sync за АЦП має бути біля V_SYNC
                bad_dc_lines = bad_dc_lines + 1 if abs(tip_est - V_SYNC) > dc_tol else 0
            else:
                # SEARCH/кандидат: фази ще нема — ставимо оцінену вершину на V_SYNC
                dc += (V_SYNC - tip_est) * g_clamp
            chunk_from = chunk_to
        # ---- 3. трекер входу
        had_broad = False
        def width_class(w):
            if BROAD_W * 0.65 <= w <= BROAD_W * 1.2: return "broad"
            if EQ_W * 0.6 <= w <= EQ_W * 1.4: return "eq"
            if SYNC_W - 0.8e-6 <= w <= SYNC_W + 0.8e-6: return "h"
            return None
        # кадр: broad-імпульси (ширина) — лише у стані LOCKED
        for (ps, pe) in pulses_pending:
            if width_class(pe - ps) == "broad":
                had_broad = True; broad_seen += 1
                if broad_seen == 3 and it_state == 2:          # третій broad-імпульс поспіль (1.5 рядка)
                    v0 = ps - 1.0 * it_T                       # початок першого broad-імпульсу
                    dph = (v0 - it_phi) % it_T
                    if 0.25 * it_T < dph < 0.75 * it_T:        # broad починається посеред рядка → поле 1, рядок 2.5
                        v_in_ref, v_in_L = v0 - 0.5 * it_T, 2
                    else:                                       # на початку рядка → поле 2, рядок 315
                        v_in_ref, v_in_L = v0, 315
                    v_locks += 1
        if it_state == 0:
            # пошук: перший імпульс H-ширини стає кандидатом; період — останній перевірений (або номінал кварцу)
            for (ps, pe) in pulses_pending:
                if width_class(pe - ps) == "h":
                    it_T = T_good if seed_toggle else T_init; seed_toggle = not seed_toggle
                    it_state = 1; it_phi = ps + it_T; it_hits = 1; it_miss = 0; q_width = 0.5; lock_lines = 0; break
        else:
            a_g, b_g = (1.0, 0.3) if it_state == 1 else (a_ph, b_T)      # кандидат: фаза = виміряна, період швидко
            # усі прогнози, що потрапляють у відрізок: для кожного — найближчий фронт у вікні ±W
            starts_arr = np.array([ps for (ps, pe) in pulses_pending]); widths = np.array([pe - ps for (ps, pe) in pulses_pending])
            while it_phi + W < chunk_to * DT:
                if len(starts_arr):
                    dd = starts_arr - it_phi
                    inwin = np.abs(dd) <= W
                    wc = np.array([width_class(w) or "" for w in widths])
                    plaus = inwin & (wc != "")
                    if plaus.any() or (inwin.any() and it_state == 2):
                        # кандидат приймає лише імпульси правдоподібної ширини; LOCKED — будь-який фронт у вікні
                        cand = np.where(plaus)[0] if plaus.any() else np.where(inwin)[0]
                        j = cand[np.argmin(np.abs(dd[cand]))]
                        e = dd[j]; cls = wc[j]
                        it_hits += 1; it_miss = 0
                        if cls in ("h", "broad"): q_width = 0.9 * q_width + 0.1
                        elif cls == "":           q_width = 0.9 * q_width
                        if cls: it_phi += a_g * e; it_T += b_g * e                 # правдоподібна ширина: фаза + період
                        else:   it_phi += 0.3 * a_g * e                           # сумнівний фронт: лише слабка корекція фази
                        it_T = float(np.clip(it_T, T_init * 0.98, T_init * 1.02))  # камера не може бути поза ±2 %
                        if it_state == 2 and q_width > 0.9 and lock_lines > 64: T_good = it_T   # перевірений період
                        it_phi += it_T
                        if it_state == 1 and it_hits >= hits_lock:
                            it_state = 2; ever_locked_t = starts_arr[j]
                            if first_lock is None: first_lock = starts_arr[j]
                        continue
                it_phi += it_T; it_miss += 1
            if it_state == 2: ever_locked_t = chunk_to * DT; lock_lines += 1
        pulses_pending = []
        if not had_broad: broad_seen = 0
        if it_miss >= miss_unlock or (it_state == 2 and (q_width < q_min or bad_dc_lines >= 16)):
            it_state = 0; it_phi = None; it_hits = 0; it_miss = 0; v_in_ref = None; q_width = 1.0; bad_dc_lines = 0
        # ---- 4. наступний вихідний рядок: період і фаза
        next_t = ot_t + ot_T
        if it_state == 2 and q_width >= 0.6:                   # вихід слідує лише за перевіреним lock (якість ширини)
            ot_T = it_T if q_width > 0.8 else T_good           # період беремо лише з перевіреного lock
            k = round((next_t - it_phi) / it_T)
            e = (it_phi + k * it_T - delay_comp) - next_t      # прошивка знає сталу затримку ФНЧ+компаратора
            step = float(np.clip(e * k_fine if abs(e) <= W else e, -slew, slew))
            next_t += step
            if v_in_ref is not None:
                kk = round((next_t - v_in_ref) / it_T)
                want = (v_in_L + kk) % 625
                delta = (want - (L + 1)) % 625
                if delta != 0:
                    # гістерезис: переставляємо лічильник лише коли два кадри поспіль просять той самий зсув
                    if v_pending == delta: L = want - 1; v_resync += 1; v_pending = None
                    else: v_pending = delta
                else: v_pending = None
                v_in_ref = None
        ot_t = next_t; L += 1
    out_starts = np.array(out_starts)
    return dict(out_starts=out_starts, kind=np.array(out_kind), state=np.array(log_state), dc=np.array(log_dc),
                T=np.array(log_T), it_phi=np.array(log_it_phi), v_resync=v_resync, v_locks=v_locks, first_lock=first_lock,
                edges_per_line=n_edges / max(1, len(out_starts)))

# ---------------- метрики (як у sim_v4) ----------------
def analyze(edges, true_starts, line_period):
    per = np.diff(edges); err_pct = (per - line_period) / line_period * 100
    bad = np.abs(err_pct) > 5.0
    run = maxrun = blue = 0
    for b in bad:
        run = run + 1 if b else 0; maxrun = max(maxrun, run)
        if run == 32: blue += 1
    ph = []; j = 0
    for e in edges:
        if e > true_starts[-1] + line_period / 2: break
        while j + 1 < len(true_starts) and true_starts[j + 1] <= e + line_period / 2: j += 1
        d = e - true_starts[j]
        if abs(d) < line_period / 2: ph.append(d)
    ph = np.array(ph) * 1e6
    return dict(lines=len(per), err_rms_pct=float(np.sqrt(np.mean(err_pct**2))), err_max_pct=float(np.max(np.abs(err_pct))),
                bad_lines=int(bad.sum()), max_bad_run=int(maxrun), blue_events=int(blue),
                phase_rms_us=float(np.sqrt(np.mean(ph**2))), phase_max_us=float(np.max(np.abs(ph)))), err_pct, ph

def relock_time(edges, true_starts, line_period, t_evt, tol=0.4e-6):
    j = 0; good = 0
    for e in edges:
        if e < t_evt: continue
        while j + 1 < len(true_starts) and true_starts[j + 1] <= e + line_period / 2: j += 1
        if abs(e - true_starts[j]) < tol: good += 1
        else: good = 0
        if good >= 20: return (e - t_evt) * 1e3
    return None

STATE_NAMES = ["SEARCH", "CANDIDATE", "LOCKED"]

def scenario(name, dur=0.30, line_period=H, snr_profile=None, dropout=None, silence=None, seed=1,
             content="bands", apl=0.4, dc_init=-0.5, ot_phase_init=0.3, **kw):
    rng = np.random.default_rng(seed)
    n_lines = int(dur / line_period) + 2
    v, starts = gen_cvbs(n_lines, line_period, apl=apl, content=content)
    t = np.arange(len(v)) * DT
    amp = np.ones_like(v); sigma = np.zeros_like(v)
    if snr_profile is None: snr_profile = lambda tt: 35.0
    snr = np.array([snr_profile(tt) for tt in t[::1000]])
    sigma = np.repeat(1.0 / (10 ** (snr / 20)), 1000)[: len(v)].astype(np.float32)
    if dropout:
        for (a, b) in dropout:
            m = (t >= a) & (t < b); amp[m] = 0.0; sigma[m] = 0.30
    if silence:
        for (a, b) in silence:
            m = (t >= a) & (t < b); amp[m] = 0.0; sigma[m] = 0.0
    noise = rng.normal(0, 1, len(v)).astype(np.float32)
    vin = v * amp + noise * sigma
    r = s2_run(vin, dur, line_period, dc_init=dc_init, ot_phase_init=ot_phase_init * line_period, **kw)
    edges = r["out_starts"]
    line_period = round(line_period * FS) / FS          # фактичний період генератора
    m, err, ph = analyze(edges, starts, line_period)
    st = r["state"]
    m["locked_pct"] = float(np.mean(st == 2) * 100); m["coast_pct"] = float(np.mean(st == 3) * 100)
    m["first_lock_ms"] = None if r["first_lock"] is None else round(r["first_lock"] * 1e3, 1)
    ev = (dropout or silence or [(None, None)])[-1][1]
    m["relock_ms"] = relock_time(edges, starts, line_period, ev) if ev else None
    m["v_resync"] = int(r["v_resync"]); m["v_locks"] = int(r["v_locks"]); m["edges_per_line"] = round(float(r["edges_per_line"]), 2)
    good = (st == 2)
    m["T_est_err_ppm"] = float((r["T"][good][-1] - line_period) / line_period * 1e6) if good.any() else None
    # джитер вихідної фази у стані LOCKED (лише де є сигнал)
    a_at = np.interp(edges[:len(ph)], t, amp)
    settled = good.copy()                      # LOCKED і минуло ≥40 рядків після входу в LOCKED (slew завершено)
    for i in np.where(np.diff(st.astype(int)) != 0)[0]: settled[i:i + 40] = False
    sel = settled[:len(ph)] & (a_at > 0.5)
    m["jitter_us_locked"] = float(np.std(ph[sel])) if sel.sum() > 10 else None
    m["dc_err_mV_max_locked"] = float(np.max(np.abs(r["dc"][good] - V_BLANK)) * 1e3) if good.any() else None
    # графік
    fig, ax = plt.subplots(4, 1, figsize=(11, 9.5), sharex=True)
    tm = edges * 1e3
    cols = np.array(["#C0392B", "#E67E22", "#2F7A4D", "#2E86C1"])[st]
    ax[0].scatter(tm[:len(ph)], ph, s=2, c=cols[:len(ph)]); ax[0].axhspan(-0.4, 0.4, color="g", alpha=.1); ax[0].set_ylim(-33, 33)
    ax[0].set_ylabel("фаза вих. sync\nvs справжній, мкс"); ax[0].set_title(f"{name}: колір = стан (червоний SEARCH, оранж. кандидат, зелений LOCKED, синій COAST)")
    ax[1].plot(tm[1:], err, lw=.6, color="#2F7A4D"); ax[1].axhspan(-5, 5, color="g", alpha=.1); ax[1].set_ylim(-8, 8); ax[1].set_ylabel("похибка періоду\nвих. рядка, %")
    ax[2].plot(tm, (r["T"] - line_period) * 1e9, lw=.8); ax[2].set_ylabel("оцінка періоду\n− справжній, нс"); ax[2].set_ylim(-400, 400)
    ax2 = ax[2].twinx(); ax2.plot(tm, (r["dc"] - V_BLANK) * 1e3, lw=.8, color="#8E44AD"); ax2.set_ylabel("помилка clamp, мВ", color="#8E44AD"); ax2.set_ylim(-600, 600)
    tt = t[::100] * 1e3
    ax[3].plot(tt, sigma[::100] * 1e3, lw=.8, label="σ шуму, мВ"); ax[3].plot(tt, amp[::100] * 300, lw=.8, label="сигнал (300=є, 0=нема)")
    ax[3].legend(loc="upper right"); ax[3].set_ylabel("вхід"); ax[3].set_xlabel("час, мс")
    fig.tight_layout(); os.makedirs("results", exist_ok=True)
    fig.savefig(f"results/S2_{name}.png", dpi=110); plt.close(fig)
    np.savez(f"results/S2_{name}.npz", vco_edges=edges, err=err, ph=ph, state=st, T=r["T"], dc=r["dc"],
             sigma=sigma[::100], amp=amp[::100], t=t[::100], starts=starts, line_period=line_period)
    return m

SCEN = {
  "A_clean":         dict(),
  "G_powerup":       dict(dur=0.5, dc_init=-1.0, ot_phase_init=0.47),
  "B_dropout":       dict(dropout=[(0.10, 0.20)]),
  "B_long_dropout":  dict(dur=1.6, dropout=[(0.20, 1.20)]),
  "C_snr_ramp":      dict(snr_profile=lambda tt: 35 - 32 * min(tt / 0.30, 1.0)),
  "H_heavy_noise":   dict(snr_profile=lambda tt: 10.0),
  "H_8dB":           dict(snr_profile=lambda tt: 8.0),
  "M_medium_noise":  dict(snr_profile=lambda tt: 14.0),
  "D_cam_64p3":      dict(line_period=64.3e-6),
  "D_cam_65p0":      dict(line_period=65.0e-6),
  "D_cam_63p0":      dict(line_period=63.0e-6),
  "D_ntsc_63p556":   dict(line_period=63.556e-6),
  "E_silence":       dict(silence=[(0.10, 0.20)]),
  "F_bursts":        dict(dur=0.4, dropout=[(0.08, 0.12), (0.16, 0.20), (0.24, 0.28)]),
  "K_darkbar":       dict(content="darkbar", dur=0.4),
  "K_darkbar_noise": dict(content="darkbar", dur=0.4, snr_profile=lambda tt: 14.0),
  "P_bright":        dict(apl=0.7, content="flat"),
}

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    names = sys.argv[1:] or list(SCEN)
    rows = []
    for nm in names:
        m = scenario(nm, **SCEN[nm]); rows.append((nm, m)); print(nm, json.dumps(m, ensure_ascii=False), flush=True)
    with open("results/S2_summary.md", "w") as f:
        f.write("| сценарій | рядків | LOCKED / COAST, % | захоплення, мс | повторний lock, мс | похибка періоду RMS/max, % | поганих (>5 %) | макс. серія | «синій» | фаза RMS/max, мкс | джитер (LOCKED), мкс | оцінка T, ppm | clamp max, мВ | V lock / resync |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for nm, m in rows:
            fmt = lambda x, d=2: "" if x is None else (round(x, d) if isinstance(x, float) else x)
            f.write(f"| {nm} | {m['lines']} | {m['locked_pct']:.0f} / {m['coast_pct']:.0f} | {fmt(m['first_lock_ms'],1)} | {fmt(m['relock_ms'],0)} | {m['err_rms_pct']:.2f} / {m['err_max_pct']:.2f} | {m['bad_lines']} | {m['max_bad_run']} | {m['blue_events']} | {m['phase_rms_us']:.2f} / {m['phase_max_us']:.2f} | {fmt(m['jitter_us_locked'],3)} | {fmt(m['T_est_err_ppm'],0)} | {fmt(m['dc_err_mV_max_locked'],0)} | {m['v_locks']} / {m['v_resync']} |\n")
    print("written results/S2_summary.md")
