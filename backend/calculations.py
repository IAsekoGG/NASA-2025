import math
import random
from typing import Dict, List
from constants import MATERIALS


def calculate_energy(size: float, speed: float, material: str) -> Dict:
    """Розрахунок кінетичної енергії"""
    mat = MATERIALS[material]
    volume = (4/3) * math.pi * (size/2)**3
    mass = volume * mat["density"]
    velocity = speed * 1000
    
    energy_j = 0.5 * mass * velocity**2
    energy_mt = energy_j / (4.184 * 10**15) * mat["strength"]
    
    # Еквіваленти
    hiroshima = energy_mt / 0.015  # 15 кілотонн
    tnt_kg = energy_mt * 1e9
    
    return {
        "energy_j": energy_j,
        "energy_mt": round(energy_mt, 3),
        "mass_kg": mass,
        "hiroshima_eq": round(hiroshima, 1),
        "tnt_kg": round(tnt_kg, 0)
    }


def calculate_crater(size: float, speed: float, angle: float, energy_mt: float) -> Dict:
    """Розрахунок кратера"""
    # Формула Коллінза-Мелоша для кратерів
    energy_factor = energy_mt ** (1/3)
    
    # Діаметр залежить від кута падіння
    angle_factor = math.sin(math.radians(angle))
    crater_diameter = 0.117 * (size ** 0.78) * (speed ** 0.44) * (angle_factor ** 0.33)
    crater_depth = crater_diameter * 0.3
    
    # Викинута порода
    ejecta_volume = math.pi * (crater_diameter/2)**2 * crater_depth
    ejecta_mass = ejecta_volume * 2500  # щільність породи
    
    return {
        "diameter_km": round(crater_diameter / 1000, 3),
        "depth_km": round(crater_depth / 1000, 3),
        "ejecta_mass_kg": round(ejecta_mass, 0),
        "rim_height_m": round(crater_depth * 0.04, 1)
    }


def calculate_airblast(energy_mt: float) -> List[Dict]:
    """Розрахунок зон ударної хвилі з наслідками"""
    zones = []
    
    # Формула для радіуса зони: R = K * E^(1/3)
    # K залежить від тиску надлишку
    
    # Зона повного знищення (> 100 кПа, 1 bar)
    r_total = 0.28 * (energy_mt ** (1/3))
    zones.append({
        "type": "total_destruction",
        "radius_km": round(r_total, 2),
        "pressure_kpa": 100,
        "effects": "Повне знищення будівель",
        "casualties": "100% летальність",
        "color": "#8B0000"
    })
    
    # Важкі руйнування (50-100 кПа)
    r_heavy = 0.4 * (energy_mt ** (1/3))
    zones.append({
        "type": "heavy_damage",
        "radius_km": round(r_heavy, 2),
        "pressure_kpa": 50,
        "effects": "Руйнування будівель, падіння стін",
        "casualties": "50-90% летальність від завалів",
        "color": "#DC143C"
    })
    
    # Середні руйнування (20-50 кПа)
    r_moderate = 0.6 * (energy_mt ** (1/3))
    zones.append({
        "type": "moderate_damage",
        "radius_km": round(r_moderate, 2),
        "pressure_kpa": 20,
        "effects": "Пошкодження дахів, падіння димарів",
        "casualties": "Травми від уламків, до 25% летальність",
        "color": "#FF4500"
    })
    
    # Легкі руйнування (5-20 кПа)
    r_light = 1.0 * (energy_mt ** (1/3))
    zones.append({
        "type": "light_damage",
        "radius_km": round(r_light, 2),
        "pressure_kpa": 5,
        "effects": "Вибиті вікна, пошкодження покрівлі",
        "casualties": "Травми від скла",
        "color": "#FFA500"
    })
    
    # Вибиті вікна (1-5 кПа)
    r_glass = 1.8 * (energy_mt ** (1/3))
    zones.append({
        "type": "glass_breakage",
        "radius_km": round(r_glass, 2),
        "pressure_kpa": 1,
        "effects": "Вибиті вікна",
        "casualties": "Легкі порізи",
        "color": "#FFD700"
    })
    
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


def calculate_tsunami(energy_mt: float, water_depth: float = 2000) -> Dict:
    """Детальний розрахунок цунамі"""
    
    # Початкова висота хвилі в епіцентрі
    initial_height = 0.1 * (energy_mt ** 0.5)
    
    # Швидкість цунамі: v = sqrt(g * d)
    g = 9.81
    wave_speed_ms = math.sqrt(g * water_depth)
    wave_speed_kmh = wave_speed_ms * 3.6
    
    # Зони впливу цунамі
    zones = []
    
    # Епіцентр
    zones.append({
        "distance_km": 0,
        "wave_height_m": round(initial_height, 1),
        "arrival_time_min": 0,
        "effects": "Початкова хвиля",
        "runup_m": round(initial_height * 2, 1)
    })
    
    # Різні відстані (хвиля зменшується з відстанню)
    for dist in [10, 50, 100, 200, 500]:
        # Висота зменшується ~ 1/sqrt(відстань)
        height = initial_height * (10 / (dist + 10)) ** 0.5
        time_min = (dist / wave_speed_kmh) * 60
        runup = height * 2.5  # Run-up зазвичай у 2-3 рази більший
        
        if height > 0.5:  # Тільки значущі хвилі
            zones.append({
                "distance_km": dist,
                "wave_height_m": round(height, 1),
                "arrival_time_min": round(time_min, 1),
                "effects": "Затоплення узбережжя",
                "runup_m": round(runup, 1)
            })
    
    return {
        "wave_speed_kmh": round(wave_speed_kmh, 1),
        "initial_height_m": round(initial_height, 1),
        "wavelength_km": round(wave_speed_ms * 15 / 1000, 1),  # Період ~15 хв
        "zones": zones,
        "warning_time_min": round((50 / wave_speed_kmh) * 60, 1)
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