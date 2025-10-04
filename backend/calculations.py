import math
import random
from typing import Dict, List
from constants import MATERIALS


# Очікується, що MATERIALS уже є в твоєму модулі
# MATERIALS = {
#     "stone": {"density": 3000, "strength": 1.0, "name": "Кам'яний"},
#     "iron":  {"density": 7800, "strength": 2.5, "name": "Залізний"},
#     "ice":   {"density":  917, "strength": 0.3, "name": "Льодяний"}
# }

TNT_J_PER_MT = 4.184e15
G_DEFAULT = 9.81
RHO_TARGET_DEFAULT = 2750

# Калібрування під твій референт: 49 м, 20 км/с, 80° → ~0.9 км
CRATER_CAL_K = 0.95  # можеш рухати в діапазоні ~0.90..1.05 під свій набір референсів

def _angle_eff(angle_deg: float) -> float:
    """Кутова ефективність для масштабування (не дозволяємо занадто малих значень)."""
    s = math.sin(math.radians(angle_deg))
    return max(0.35, s)  # клемп, щоб дуже пологі не занулювали все

def calculate_energy(size: float, speed: float, material: str) -> Dict:
    """
    Кінетична енергія. size — діаметр м, speed — км/с.
    Повертає старий формат, який у тебе вже споживається фронтом.
    """
    mat = MATERIALS[material]
    volume = (4/3) * math.pi * (size/2)**3
    mass = volume * mat["density"]
    v = speed * 1000.0

    energy_j = 0.5 * mass * v**2
    energy_mt = energy_j / TNT_J_PER_MT

    hiroshima = energy_mt / 0.015
    tnt_kg = energy_mt * 1e9

    print(f"\n[ENERGY] d={size}м, v={speed}км/с, material={material}")
    print(f"[ENERGY] mass={mass:.3e}кг, volume={volume:.1f}м³")
    print(f"[ENERGY] E={energy_j:.3e}Дж = {energy_mt:.3f}Мт")

    return {
        "energy_j": energy_j,
        "energy_mt": round(energy_mt, 3),
        "mass_kg": mass,
        "hiroshima_eq": round(hiroshima, 1),
        "tnt_kg": round(tnt_kg, 0),
    }

def calculate_crater(
    size: float,
    speed: float,
    angle: float,
    rho_i: float = 3000,
    rho_t: float = RHO_TARGET_DEFAULT,
    g: float = G_DEFAULT,
) -> Dict:
    """
    Розрахунок ФІНАЛЬНОГО простого кратера (rim-to-rim).
    ПОВЕРТАЄ СТАРІ КЛЮЧІ:
      - diameter_km (float)
      - depth_km (float)
      - ejecta_mass_kg (float)
      - rim_height_m (float)
    Плюс допоміжні: shape, width_km, length_km, energy_mt.
    """
    print("\n" + "="*64)
    print("РОЗРАХУНОК КРАТЕРА (сумісний формат)")
    print(f"Input: size={size}м, speed={speed}км/с, angle={angle}°; rho_i={rho_i}, rho_t={rho_t}, g={g}")

    v = speed * 1000.0
    theta = math.radians(angle)
    sin_theta = math.sin(theta)

    # Маса та енергія
    volume = (4/3) * math.pi * (size/2)**3
    mass = rho_i * volume
    E = 0.5 * mass * v**2
    E_mt = E / TNT_J_PER_MT

    # π-скейлінг (Collins–Melosh) для транзієнтного діаметра (м)
    # ВАЖЛИВО: слабка залежність від кута: (sinθ)^(1/3)
    D_tr = 1.161 * ((rho_i/rho_t) ** (1/3)) * (size ** 0.783) \
           * (v ** 0.44) * (g ** -0.217) * (sin_theta ** (1/3))

    # Фінальний діаметр (простий кратер)
    D_final = 1.25 * D_tr

    # Кутова корекція (без подвійного множення sinθ по енергії!)
    eff = _angle_eff(angle)  # 0.35..1.0
    if angle < 30:
        D_final *= (0.85 * eff + 0.10)  # помірно зменшуємо при дуже пологих
    else:
        D_final *= (0.95 + 0.05 * eff)  # для крутих майже без змін

    # Глобальна калібровка
    D_final *= CRATER_CAL_K

    # Форма/еліпс для дуже пологих
    shape = "circular"
    width_m = D_final
    length_m = D_final
    if angle < 30:
        elong = min(1.0/max(1e-6, sin_theta), 3.0)  # cap ×3
        shape = "elliptical"
        width_m = D_final
        length_m = D_final * elong

    # Глибина/вал
    if angle < 30:
        depth_m = 0.2 * D_final * sin_theta   # мілкіше при пологих
    else:
        depth_m = 0.2 * D_final * (0.9 + 0.1 * eff)
    rim_h_m = 0.04 * D_final

    # Маса викидів (груба оцінка)
    crater_area = math.pi * (D_final/2)**2
    ejecta_volume = crater_area * depth_m
    ejecta_mass = ejecta_volume * rho_t

    print(f"[CRATER] D_tr={D_tr:.1f}м → D_final={D_final:.1f}м ({D_final/1000:.3f}км), shape={shape}")
    if shape == "elliptical":
        print(f"[CRATER] width={width_m:.1f}м, length={length_m:.1f}м, elong≈{length_m/width_m:.2f}")
    print(f"[CRATER] depth≈{depth_m:.1f}м ({depth_m/1000:.3f}км), rim≈{rim_h_m:.1f}м")
    print(f"[CRATER] ejecta_mass≈{ejecta_mass:.3e}кг; energy≈{E_mt:.3f}Мт")

    # КЛЮЧОВЕ: diameter_km ІСНУЄ ЗАВЖДИ (беремо «ширину» як базовий діаметр)
    result = {
        "diameter_km": round(width_m / 1000.0, 3),
        "depth_km": round(depth_m / 1000.0, 3),
        "ejecta_mass_kg": round(ejecta_mass, 0),
        "rim_height_m": round(rim_h_m, 1),
        # додаткові:
        "shape": shape,
        "width_km": round(width_m / 1000.0, 3),
        "length_km": round(length_m / 1000.0, 3),
        "energy_mt": round(E_mt, 3),
    }
    return result

import math
from typing import Dict, List, Optional

def calculate_airblast(
    energy_mt: float,
    *,
    burst_mode: str = "surface",          # "surface" | "air" | "auto"
    burst_height_m: Optional[float] = None,  # висота підриву для "air", м
) -> List[Dict]:
    """
    Реалістичні зони ударної хвилі (надлишковий тиск) з масштабуванням ~ E^(1/3).
    Повертає той самий формат (type, radius_km, pressure_kpa, effects, casualties, color),
    + додатково: wind_ms, notes (не ламає фронт).

    ПАРАМЕТРИ:
      energy_mt     — еквівалент енергії вибуху в мегатоннах ТНТ (>=0)
      burst_mode    — "surface" (за замовч.), "air", "auto"
      burst_height_m— висота підриву (м) для "air"; якщо None і "air"/"auto" → оберемо оптимальну HOB

    ОСНОВА:
      - Базові радіуси для 1 Мт (поверхневий вибух), км:
          100 кПа ≈ 3.0, 50 кПа ≈ 4.5, 20 кПа ≈ 7.0, 5 кПа ≈ 12.0, 1 кПа ≈ 20.0
      - Масштабування: R = R0 * E^(1/3).
      - Для повітряного підриву враховуємо «оптимальну висоту» (HOB), що найбільше розширює
        зони середніх/малих тисків (ефект Маха). Робимо це через просту гладку поправку.
    """
    # захист від нулів/некоректних значень
    E_mt = max(float(energy_mt), 0.0)
    E13 = (E_mt if E_mt > 1e-9 else 1e-9) ** (1/3)  # кубічний корінь для масштабування

    # БАЗОВІ РАДІУСИ (км) для 1 Мт ПО-ЗЕМЛІ (surface burst)
    # ці значення близькі до узагальнених ядерних таблиць для рівня землі
    base_surface = {
        100: 3.0,   # ≈14.5 psi
        50:  4.5,   # ≈7.3  psi
        20:  7.0,   # ≈2.9  psi
        5:   12.0,  # ≈0.73 psi
        1:   20.0,  # ≈0.15 psi
    }

    # ОПТИМАЛЬНА ВИСОТА ПОВІТРЯНОГО ПІДРИВУ (HOB) ДЛЯ МАКСИМУМУ РАДІУСУ певного тиску (на 1 Мт, у км)
    # наближені значення: високі тиски нижче, малі тиски вище
    opt_hob_km_1Mt = {
        100: 0.5,
        50:  1.0,
        20:  1.8,
        5:   3.0,
        1:   7.0,
    }

    # "Посилення" радіуса від повітряного підриву поблизу оптимуму (множники при максимумі)
    # для високих тисків ефект невеликий, для 5–1 кПа помітний.
    # Також для 100 кПа ми навіть трохи "штрафуємо" — надвисокі тиски менші при HOB.
    hob_peak_gain = {
        100: 0.00,  # -0% (можна навіть -0.1, якщо хочеш)
        50:  0.10,  # +10%
        20:  0.20,  # +20%
        5:   0.35,  # +35%
        1:   0.25,  # +25%
    }
    # ширина "дзвоника" навколо оптимуму (скільки км в масштабі 1 Мт)
    hob_sigma_km_1Mt = {
        100: 0.6,
        50:  1.0,
        20:  1.6,
        5:   2.5,
        1:   4.0,
    }

    # Якщо в режимі "air" або "auto", нам потрібна висота. Якщо None — оберемо опт для 5 кПа.
    # Масштабуємо оптимум з 1 Мт до потрібної енергії: H_opt(E) ~ H_opt(1Mt) * E^(1/3)
    auto = (burst_mode in ("air", "auto"))
    if auto and burst_height_m is None:
        # максимізація зони важких руйнувань (5 кПа) — типова задача "оптимального HOB"
        opt_h_km = opt_hob_km_1Mt[5] * E13
        burst_height_m = opt_h_km * 1000.0

    # корисні допоміжні
    def airburst_multiplier(pressure_kpa: int, H_m: float) -> float:
        """
        Гладка поправка для повітряного підриву: 1 + gain * exp(- (ΔH)^2 / (2σ^2)),
        де ΔH — різниця між H і оптимальною HOB для цього тиску.
        Якщо режим surface → множник = 1.
        """
        if burst_mode == "surface" or H_m is None:
            return 1.0
        # масштабовані параметри для поточного E
        opt_km = opt_hob_km_1Mt[pressure_kpa] * E13
        sigma_km = hob_sigma_km_1Mt[pressure_kpa]
        gain = hob_peak_gain[pressure_kpa]
        H_km = H_m / 1000.0
        d = (H_km - opt_km)
        # гаусів "дзвоник" навколо оптимуму
        m = 1.0 + gain * math.exp(-0.5 * (d / sigma_km) ** 2)
        return max(0.7, m)  # не даємо впасти нижче 0.7 × surface

    # ШВИДКІСТЬ ВІТРУ при даному тиску (грубе наближення для пікової швидкості, м/с)
    # Значення підібрані за довідковими кривими: 1 кПа ~ 35–45 м/с; 5 кПа ~ 70–110; 20 кПа ~150–190; 50 кПа ~220–260; 100 кПа ~280–320
    wind_lookup = {
        1:   (35, 45),
        5:   (80, 110),
        20:  (150, 190),
        50:  (220, 260),
        100: (280, 320),
    }
    def wind_mid_ms(p_kpa: int) -> int:
        lo, hi = wind_lookup[p_kpa]
        return int(round((lo + hi) / 2))

    # ОПИС НАСЛІДКІВ — акуратний, реалістний
    effects_map = {
        100: ("Майже повне знищення будівель; бетон/цегла руйнуються.", "Дуже висока летальність"),
        50:  ("Важкі руйнування: обвал стін, перекриттів; перекидання важкого транспорту.", "Високі втрати"),
        20:  ("Серйозні пошкодження: частковий обвал, травми від уламків.", "Помірні–високі втрати"),
        5:   ("Легкі–помірні пошкодження: вибиті вікна, пошкоджені дахи, травми осколками.", "Низькі–помірні втрати"),
        1:   ("Масове биття скла; легкі поранення уламками скла.", "Низькі"),
    }
    color_map = {
        100: "#8B0000",
        50:  "#DC143C",
        20:  "#FF4500",
        5:   "#FFA500",
        1:   "#FFD700",
    }

    # РОЗРАХУНОК
    pressures = [100, 50, 20, 5, 1]  # кПа
    zones: List[Dict] = []
    for p in pressures:
        base_km = base_surface[p]
        # поверхневий базовий радіус, масштабований по E^(1/3)
        R_km_surface = base_km * E13
        # мультиплікатор для airburst (якщо застосовний)
        mult = airburst_multiplier(p, burst_height_m)
        R_km = R_km_surface * mult

        # запис зони (старі ключі збережені)
        wind = wind_mid_ms(p)
        eff_txt, cas_txt = effects_map[p]
        zones.append({
            "type": (
                "total_destruction" if p == 100 else
                "heavy_damage"      if p == 50  else
                "moderate_damage"   if p == 20  else
                "light_damage"      if p == 5   else
                "glass_breakage"
            ),
            "radius_km": round(R_km, 2),
            "pressure_kpa": p,
            "effects": eff_txt,
            "casualties": cas_txt,
            "color": color_map[p],
            # нові, не обов'язкові:
            "wind_ms": wind,
            "notes": (
                "Поверхневий вибух" if burst_mode == "surface"
                else f"Повітряний вибух, HOB≈{int(round((burst_height_m or 0)/1000))} км, множник {mult:.2f}"
            ),
        })

        # DEBUG
        print(f"[AIRBLAST] {p:>3} кПа: R_surf≈{R_km_surface:.2f} км → R≈{R_km:.2f} км "
              f"(mode={burst_mode}, mult={mult:.2f}), wind~{wind} м/с")

    return zones


def calculate_thermal(energy_mt: float, altitude_km: float = 0) -> List[Dict]:
    """Розрахунок теплового випромінювання"""
    zones = []
    
    
    # Третій ступінь опіків (повна товщина шкіри)
    thermal_3rd = 0.6 * (energy_mt ** 0.41)
    zones.append({
        "type": "third_degree_burns",
        "radius_km": round(thermal_3rd, 2),
        "temperature_c": 2000,
        "effects": "Опіки 3-го ступеня",
        "casualties": "Критичні опіки, висока летальність",
        "ignition": "Займання всього легкозаймистого",
        "color": "#FF0000"
    })
    
    # Другий ступінь опіків
    thermal_2nd = 0.9 * (energy_mt ** 0.41)
    zones.append({
        "type": "second_degree_burns",
        "radius_km": round(thermal_2nd, 2),
        "temperature_c": 1000,
        "effects": "Опіки 2-го ступеня",
        "casualties": "Важкі опіки, потрібна госпіталізація",
        "ignition": "Займання одягу, дерева",
        "color": "#FF6347"
    })
    
    # Перший ступінь опіків
    thermal_1st = 1.5 * (energy_mt ** 0.41)
    zones.append({
        "type": "first_degree_burns",
        "radius_km": round(thermal_1st, 2),
        "temperature_c": 400,
        "effects": "Опіки 1-го ступеня",
        "casualties": "Болючі, але не небезпечні для життя",
        "ignition": "Почервоніння шкіри",
        "color": "#FFA07A"
    })
    
    return zones


def calculate_seismic(energy_mt: float) -> List[Dict]:
    """Розрахунок сейсмічних ефектів"""
    zones = []
    
    # Магнітуда землетрусу за шкалою Рихтера
    magnitude = 0.67 * math.log10(energy_mt) + 4.87
    
    # MMI шкала на різних відстанях
    mmi_zones = [
        {"mmi": 12, "radius": 0.1 * (energy_mt ** 0.33), "effects": "Тотальне знищення, зміщення ґрунту", "color": "#4B0082"},
        {"mmi": 10, "radius": 0.3 * (energy_mt ** 0.33), "effects": "Руйнування більшості споруд", "color": "#8B008B"},
        {"mmi": 8, "radius": 0.6 * (energy_mt ** 0.33), "effects": "Значні пошкодження будівель", "color": "#9370DB"},
        {"mmi": 6, "radius": 1.2 * (energy_mt ** 0.33), "effects": "Відчутні струси, тріщини", "color": "#BA55D3"},
        {"mmi": 4, "radius": 2.5 * (energy_mt ** 0.33), "effects": "Помітні коливання", "color": "#DDA0DD"}
    ]
    
    for zone in mmi_zones:
        zones.append({
            "type": f"seismic_mmi_{zone['mmi']}",
            "radius_km": round(zone["radius"], 2),
            "mmi": zone["mmi"],
            "magnitude_richter": round(magnitude, 2),
            "effects": zone["effects"],
            "color": zone["color"]
        })
    
    return zones



def calculate_tsunami(
    energy_mt: float,
    water_depth_m: float = 4000.0,  # глибоке море
    period_min: float = 15.0        # для довжини хвилі (інформаційно)
) -> Dict:
    """
    Прості 'кільця цунамі' для мапи: радіуси за порогами офшорної висоти хвилі.
    БЕЗ пошуку узбереж, без складних шолінгів — тільки наочні зони.
    """
    g = 9.81
    E_mt = max(0.0, float(energy_mt))

    # 1) Офшорна швидкість і довжина хвилі (інфо)
    c_ms = math.sqrt(g * water_depth_m)
    c_kmh = c_ms * 3.6
    T_s = period_min * 60.0
    wavelength_km = (c_ms * T_s) / 1000.0

    # 2) Початкова офшорна висота біля епіцентра (проста енергетична оцінка)
    K = 0.25
    H0 = K * math.sqrt(E_mt)           # м
    r0 = 10.0                          # км, стабілізація центру

    # 3) Пороги офшорної висоти для кілець (м)
    thresholds = [
        ("tsunami_extreme",    30.0,   "#6b0000", "Негайна евакуація. Високий ризик затоплення >10 м у прибережних низинах."),
        ("tsunami_major",      15,   "#a50000", "Евакуація на висоти >20 м. Багаторазові хвилі, сильні течії."),
        ("tsunami_moderate",   7,   "#d45500", "Уникати берегової лінії, гаваней, мостів. Підвищена обережність."),
        ("tsunami_minor",      3,   "#f6a800", "Можливі затоплення низин, небезпечні течії в портах."),
        ("tsunami_information",0.0,   "#ffd166", "Слабкі коливання рівня, локальні течії."),
    ]
    # 4) Знаходження радіуса для порогу H_thr:
    #    H(r) = H0 * sqrt(r0/(r+r0)) ⇒ r = r0 * (H0/H_thr)^2 - r0
    def radius_for(H_thr: float) -> float:
        if H_thr <= 0:
            return 4.0 * r0  # просто велике зовнішнє кільце
        if H0 <= 1e-9:
            return 0.0
        r = r0 * (H0 / H_thr)**2 - r0
        return max(0.0, r)

    zones: List[Dict] = []
    prev_radius = 0.0
    for label, H_thr, color, advice in thresholds:
        R = radius_for(H_thr)
        # монотонізуємо (щоб не було накладання при малих E)
        R = max(R, prev_radius)
        prev_radius = R

        eta_min = (R / c_kmh) * 60.0 if c_kmh > 1e-6 else float('inf')
        zones.append({
            "type": label,
            "radius_km": round(R, 1),
            "wave_height_m": round(H_thr, 2),  # порогова офшорна висота на межі кільця
            "arrival_time_min": round(eta_min, 1),
            "advice": advice,
            "color": color,
        })

    return {
        "wave_speed_kmh": round(c_kmh, 1),
        "wavelength_km": round(wavelength_km, 1),
        "initial_height_m": round(H0, 2),
        "zones": zones
    }


def calculate_fragmentation(size: float, speed: float, material: str, fragments: int = 3) -> Dict:
    """Розрахунок для розколу на фрагменти"""
    total_energy = calculate_energy(size, speed, material)
    
    # Розподіл енергії між фрагментами (більший отримує більше)
    fragment_data = []
    
    for i in range(fragments):
        # Розмір фрагмента (найбільший ~40%, інші менші)
        size_factor = (fragments - i) / fragments
        frag_size = size * (size_factor ** 0.7)
        frag_energy_mt = total_energy["energy_mt"] * (size_factor ** 1.5) / sum([(fragments - j) ** 1.5 for j in range(fragments)])
        
        # Відстань між точками удару (залежить від висоти розпаду)
        separation_km = random.uniform(2, 10) * (i + 1)
        
        fragment_data.append({
            "id": i + 1,
            "size_m": round(frag_size, 1),
            "energy_mt": round(frag_energy_mt, 3),
            "separation_km": round(separation_km, 1),
            "blast_radius_km": round(0.5 * (frag_energy_mt ** (1/3)), 2)
        })
    
    return {
        "fragments": fragment_data,
        "total_energy_mt": total_energy["energy_mt"],
        "fragmentation_altitude_km": round(20 + random.uniform(-5, 5), 1)
    }