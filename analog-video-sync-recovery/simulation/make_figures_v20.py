#!/usr/bin/env python3
"""Рисунки для Системи 2.0 з results/S2_*.npz (після sim_v20.py) та порівняння з v6 (results/V6_*.npz).
Панель «екран»: рядок тестової картинки зсунуто на реальну фазову похибку вихідного sync (5 px = 1 мкс);
під час пропадання — шум; синій — ≥32 рядки підряд з похибкою періоду >5 %. Ліва смужка = стан трекера."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sim_v20 as S

RED, ORG, GRN, BLU = "#C0392B", "#E67E22", "#2F7A4D", "#2E5AAC"
def load(n): return dict(np.load(f"results/{n}.npz"))

def screen(d, step=6, W=260):
    ph = d["ph"]; err = d["err"]; edges = d["vco_edges"]
    n = min(len(ph), len(err)); ph = ph[:n]; err = err[:n]; edges = edges[1:n + 1]
    t = d["t"]; amp = d["amp"]; sigma = d["sigma"]
    st = d["state"][:n] if "state" in d else np.full(n, 2)
    rng = np.random.default_rng(3)
    x = np.arange(W); base = np.zeros((W, 3))
    cols = [(0.85, 0.85, 0.85), (0.9, 0.75, 0.2), (0.2, 0.6, 0.9), (0.3, 0.7, 0.35)]
    for i, c in enumerate(cols): base[(x * 4 // W) == i] = c
    rows = []; bad_run = 0; blue = []; states = []
    for k in range(0, n, step):
        a = np.interp(edges[k], t, amp); s = np.interp(edges[k], t, sigma)
        bad_run = bad_run + step if abs(err[k]) > 5 else 0
        isblue = bad_run >= 32
        if isblue: row = np.tile([[0.05, 0.15, 0.75]], (W, 1))
        elif a < 0.5: row = np.tile(rng.uniform(0.15, 0.85, (W, 1)), (1, 3))
        else:
            dx = int(round(ph[k] * 5)); row = np.roll(base, dx, axis=0).copy()
            if s > 0.12: row = np.clip(row + rng.normal(0, min(s, 0.5), (W, 1)), 0, 1)
            if abs((k / n) - 0.5) < 0.02: row[:] = [0.1, 0.1, 0.1]
        rows.append(row); blue.append(isblue); states.append(st[k])
    return np.array(rows), np.array(blue), edges[::step] * 1e3, np.array(states)

def panel_screen(ax, d, title, strip=True):
    img, blue, tm, st = screen(d)
    ax.imshow(img, aspect="auto", extent=[0, 52, tm[-1], tm[0]], interpolation="nearest")
    if strip:
        cmap = np.array([[0.75, 0.22, 0.17], [0.9, 0.49, 0.13], [0.18, 0.48, 0.30], [0.18, 0.53, 0.76]])
        ax.imshow(cmap[st][:, None, :], aspect="auto", extent=[-3.5, -0.5, tm[-1], tm[0]], interpolation="nearest")
        ax.set_xlim(-3.5, 52)
    ax.set_title(title, fontsize=10, loc="left"); ax.set_xlabel("ширина кадру, мкс"); ax.set_ylabel("час, мс ↓")
    return int(blue.sum())

def note(ax, txt, xy, xytext, color=RED):
    ax.annotate(txt, xy=xy, xycoords="axes fraction", xytext=xytext, textcoords="axes fraction", fontsize=9, color=color,
                arrowprops=dict(arrowstyle="->", color=color, lw=1), bbox=dict(boxstyle="round,pad=.3", fc="white", ec=color, alpha=.92))

# ---------- Рис. 9: Система 2.0 — шість сценаріїв, що бачить монітор ----------
cases = [("A_clean", "чистий сигнал 35 дБ (з увімкнення)"), ("B_dropout", "пропадання 100 мс (сніг на вході)"),
         ("C_snr_ramp", "SNR 35 → 3 дБ за 300 мс"), ("D_cam_65p0", "камера 65.0 мкс (+1.6 %)"),
         ("H_heavy_noise", "постійний шум 10 дБ"), ("F_bursts", "три пропадання по 40 мс")]
fig, ax = plt.subplots(2, 3, figsize=(15, 10))
for a, (nm, ttl) in zip(ax.flat, cases):
    d = load("S2_" + nm); nb = panel_screen(a, d, f"{ttl}\n«синіх»: {nb}" if False else ttl)
    nb = int(screen(d)[1].sum()); a.set_title(f"{ttl}   [синіх екранів: {nb}]", fontsize=10, loc="left")
note(ax[0, 0], "≈3.4 мс від увімкнення: SEARCH → LOCKED,\nпідхід до фази входу зі slew 1 мкс/рядок", (0.5, 0.97), (0.3, 0.75), GRN)
note(ax[0, 1], "COAST: sync іде далі від кварцу,\nна екрані сніг, не синій", (0.5, 0.5), (0.2, 0.8), GRN)
note(ax[0, 1], "повернення: повторний lock за 4 мс,\nslew ≤32 рядки, картинка на місці", (0.5, 0.33), (0.2, 0.15), GRN)
note(ax[0, 2], "до ~8 дБ рівні краї (джитер ≤0.2 мкс);\nнижче — окремі промахи, без синього", (0.5, 0.7), (0.15, 0.9), GRN)
note(ax[1, 0], "період 65.0 оцінено з похибкою 3 ppm:\nжодного зсуву — на відміну від v5/v6", (0.5, 0.55), (0.12, 0.85), GRN)
fig.suptitle("Рис. 9. Система 2.0: що бачить монітор у шести сценаріях (смужка зліва: червоний SEARCH, оранжевий кандидат, зелений LOCKED, синій COAST)", fontsize=12, x=0.02, ha="left")
fig.tight_layout(); fig.savefig("results/FIG9_s2_screens.png", dpi=120); plt.close(fig)

# ---------- Рис. 10: v6 проти 2.0 на важких сценаріях ----------
pairs = [("D_cam_65p0", "камера 65.0 мкс"), ("H_heavy_noise", "шум 10 дБ постійно"), ("B_long_dropout", "пропадання 1 с")]
fig, ax = plt.subplots(2, 3, figsize=(15, 10))
for j, (nm, ttl) in enumerate(pairs):
    try:
        d6 = load("V6_" + nm); nb6 = int(screen(d6)[1].sum())
        panel_screen(ax[0, j], d6, f"ДО (v6 NE555+CD4046): {ttl}   [синіх: {nb6}]", strip=False)
        ax[0, j].title.set_color(RED)
    except FileNotFoundError:
        ax[0, j].text(0.5, 0.5, "v6: результату нема", ha="center"); ax[0, j].set_axis_off()
    d2 = load("S2_" + nm); nb2 = int(screen(d2)[1].sum())
    panel_screen(ax[1, j], d2, f"ПІСЛЯ (Система 2.0): {ttl}   [синіх: {nb2}]"); ax[1, j].title.set_color(GRN)
note(ax[0, 0], "v6: VCO не знає періоду камери,\nкожен рядок запускає VCO → зсув\nна пів рядка, сходинки", (0.5, 0.5), (0.05, 0.85))
note(ax[1, 0], "2.0: період — з кварцу і оцінки\nвходу (PI); картинка рівна", (0.5, 0.5), (0.1, 0.85), GRN)
note(ax[0, 1], "v6: LM1881 губить 40 % імпульсів —\nрядки хаотично зсунуті", (0.5, 0.5), (0.05, 0.85))
note(ax[1, 1], "2.0: зріз посередині + вікно ±1.5 мкс:\nвикиди не проходять", (0.5, 0.5), (0.1, 0.85), GRN)
note(ax[1, 2], "1 с COAST: sync іде від кварцу на останньому\nперевіреному періоді; повернення — lock за 4 мс + slew", (0.5, 0.5), (0.05, 0.85), GRN)
fig.suptitle("Рис. 10. Ті самі сценарії: останній дискретний варіант (v6) проти Системи 2.0", fontsize=12, x=0.02, ha="left")
fig.tight_layout(); fig.savefig("results/FIG10_v6_vs_s2.png", dpi=120); plt.close(fig)

# ---------- Рис. 11: один рядок — вхід, гілка компаратора, строб, вихід ----------
rng = np.random.default_rng(7)
v, starts = S.gen_cvbs(30, S.H)
sigma = 1 / 10**(14 / 20)
vin = v + rng.normal(0, 1, len(v)).astype(np.float32) * sigma
y = S.lpf1(vin, 300e3)
k = 25; L = int(S.H * S.FS); i0 = k * L - int(6e-6 * S.FS); i1 = k * L + int(70e-6 * S.FS)
t = (np.arange(i0, i1) - k * L) * S.DT * 1e6
node = vin[i0:i1] + S.V_BLANK; comp_in = y[i0:i1] + S.V_BLANK
cs = comp_in < S.V_THR
def debounce(c, w=5):                       # злити провали < w відліків, відкинути імпульси < w відліків
    c = c.copy()
    for val in (True, False):
        i = 0
        while i < len(c):
            j = i
            while j < len(c) and c[j] == val: j += 1
            if 0 < j - i < w and i > 0 and j < len(c): c[i:j] = not val
            i = max(j, i + 1)
    return c
cs = debounce(cs)
out = node.copy(); m = (t >= 0) & (t < 4.7); out[m] = S.V_SYNC
fig, ax = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
ax[0].plot(t, node, lw=.6, color="0.3"); ax[0].axhline(S.V_BLANK, color=BLU, lw=.8, ls="--"); ax[0].axhline(S.V_SYNC, color=BLU, lw=.8, ls=":")
ax[0].set_ylabel("вузол після clamp, В"); ax[0].set_title("Вхід (SNR 14 дБ): CVBS після конденсатора, DC відновлено keyed clamp'ом (blanking = 0.60 В)", fontsize=10, loc="left")
ax[0].axvspan(8.2, 9.4, color=BLU, alpha=.2); ax[0].annotate("строб CLAMP 8.2–9.4 мкс", xy=(8.8, 1.5), xytext=(14, 1.75), color=BLU, fontsize=8, arrowprops=dict(arrowstyle="->", color=BLU, lw=.8))
ax[1].plot(t, comp_in, lw=.7, color="0.3"); ax[1].axhline(S.V_THR, color=RED, lw=.9); ax[1].text(20, S.V_THR + 0.03, "поріг 0.45 В = посередині між вершиною і blanking", color=RED, fontsize=8)
ax[1].set_ylabel("вхід компаратора, В"); ax[1].set_title("Гілка компаратора: ФНЧ 300 кГц (не в тракті відео) → зріз 50 %; стала затримка 0.6 мкс компенсується у прошивці", fontsize=10, loc="left")
ax[2].step(t, cs.astype(int), lw=1, color=GRN); ax[2].set_ylim(-0.2, 1.4); ax[2].set_ylabel("COMP → таймер")
ax[2].set_title("Вихід компаратора: MCU міряє фронти й ширину (4.7 мкс = H, 2.35 = eq, 27.3 = broad), дебаунс 0.5 мкс", fontsize=10, loc="left")
ax[2].axvspan(-1.5, 1.5, color=GRN, alpha=.15); ax[2].text(1.8, 1.15, "вікно ±1.5 мкс навколо прогнозу", color=GRN, fontsize=8)
ax[3].plot(t, out, lw=.6, color="0.3"); ax[3].plot(t[m], out[m], lw=2, color=GRN)
ax[3].set_ylabel("вихід (до буфера), В"); ax[3].set_xlabel("час від початку рядка, мкс")
ax[3].set_title("Вихід: SPDT підставляє V_SYNC лише на 0–4.7 мкс синтетичної шкали; порч, burst і відео — як на вході", fontsize=10, loc="left")
ax[3].axvspan(5.6, 7.85, color="orange", alpha=.15); ax[3].text(5.7, 0.95, "burst\nне чіпаємо", fontsize=8, color="#B9770E")
for a in ax: a.grid(alpha=.2)
fig.suptitle("Рис. 11. Один рядок у Системі 2.0: що робить аналогова частина", fontsize=12, x=0.02, ha="left")
fig.tight_layout(); fig.savefig("results/FIG11_s2_one_line.png", dpi=120); plt.close(fig)

# ---------- Рис. 12: увімкнення з поганим DC та пропадання 1 с — стан, фаза, clamp, період ----------
fig, ax = plt.subplots(3, 2, figsize=(14, 9), sharex="col")
for j, (nm, ttl, xl) in enumerate([("G_powerup", "увімкнення: конденсатор −1 В, фаза випадкова", (0, 60)), ("B_long_dropout", "пропадання 200–1200 мс (1 с снігу)", (0, 1600))]):
    d = load("S2_" + nm); tm = d["vco_edges"] * 1e3; st = d["state"]; ph = d["ph"]
    cols = np.array([RED, ORG, GRN, "#2E86C1"])[st]
    ax[0, j].scatter(tm[:len(ph)], ph, s=3, c=cols[:len(ph)]); ax[0, j].set_ylim(-34, 34); ax[0, j].axhspan(-0.4, 0.4, color="g", alpha=.12)
    ax[0, j].set_ylabel("фаза вих. sync\nvs справжній, мкс"); ax[0, j].set_title(ttl, fontsize=11, fontweight="bold", loc="left")
    ax[1, j].plot(tm, (d["dc"] - S.V_BLANK) * 1e3, lw=.9, color="#8E44AD"); ax[1, j].set_ylabel("помилка clamp, мВ"); ax[1, j].axhspan(-30, 30, color="g", alpha=.12)
    ax[2, j].plot(tm, (d["T"] - d["line_period"]) * 1e9, lw=.9); ax[2, j].set_ylabel("оцінка періоду −\nсправжній, нс"); ax[2, j].set_xlabel("час, мс"); ax[2, j].set_ylim(-300, 300)
    for a in ax[:, j]: a.set_xlim(*xl); a.grid(alpha=.2)
    if nm == "B_long_dropout":
        for a in ax[:, j]: a.axvspan(200, 1200, color="0.6", alpha=.2)
note(ax[0, 0], "SEARCH: АЦП ставить вершину sync на V_SYNC,\nкандидати відкидаються, поки DC не сів", (0.08, 0.85), (0.3, 0.6))
note(ax[0, 0], "LOCKED → slew 1 мкс/рядок до фази входу", (0.15, 0.55), (0.45, 0.3), GRN)
note(ax[1, 0], "SEARCH: DC за оцінкою вершини (АЦП);\nLOCKED: keyed clamp, далі ±30 мВ", (0.1, 0.4), (0.4, 0.75), "#8E44AD")
note(ax[0, 1], "1 с без сигналу: sync генерується далі від кварцу.\nСходинки = короткі хибні lock на шумі зсувають фазу;\nкартинки нема, тож невидимо; на повернення не впливає", (0.45, 0.6), (0.12, 0.88), GRN)
note(ax[2, 1], "COAST тримає останню оцінку; після повернення\nоцінка поновлюється за кілька рядків", (0.75, 0.55), (0.25, 0.85), GRN)
fig.suptitle("Рис. 12. Захоплення з нуля і довге пропадання: стан трекера, clamp, оцінка періоду", fontsize=12, x=0.02, ha="left")
fig.tight_layout(); fig.savefig("results/FIG12_s2_powerup_longdrop.png", dpi=120); plt.close(fig)
print("FIG9–12 written")
