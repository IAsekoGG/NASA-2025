import math
from typing import Dict, List

# Апроксимація густини населення по регіонах (люд/км²)
POPULATION_DENSITY_REGIONS = {
    # Європа
    "europe_urban": 3000, "europe_suburban": 800, "europe_rural": 100,
    # Азія
    "asia_megacity": 15000, "asia_urban": 5000, "asia_suburban": 1200, "asia_rural": 200,
    # Америка
    "americas_urban": 2500, "americas_suburban": 600, "americas_rural": 50,
    # Африка
    "africa_urban": 4000, "africa_suburban": 900, "africa_rural": 80,
    # Океанія
    "oceania_urban": 1800, "oceania_suburban": 400, "oceania_rural": 5,
}

# Економічна вартість інфраструктури ($/км²)
INFRASTRUCTURE_VALUE = {
    "megacity": 500_000_000,      # $500M/км²
    "urban_dense": 100_000_000,   # $100M/км²
    "urban": 30_000_000,          # $30M/км²
    "suburban": 5_000_000,        # $5M/км²
    "rural": 500_000,             # $0.5M/км²
    "industrial": 200_000_000,    # $200M/км²
}


def estimate_population_density(lat: float, lon: float) -> Dict:
    """Оцінка густини населення на основі координат"""
    
    # Великі міста світу (апроксимація)
    major_cities = [
        {"name": "Токіо", "lat": 35.6, "lon": 139.7, "density": 15000},
        {"name": "Дакка", "lat": 23.8, "lon": 90.4, "density": 20000},
        {"name": "Манхеттен", "lat": 40.7, "lon": -74.0, "density": 28000},
        {"name": "Мумбаї", "lat": 19.0, "lon": 72.8, "density": 20000},
        {"name": "Київ", "lat": 50.4, "lon": 30.5, "density": 3500},
        {"name": "Лондон", "lat": 51.5, "lon": -0.1, "density": 5700},
        {"name": "Париж", "lat": 48.8, "lon": 2.3, "density": 21000},
        {"name": "Москва", "lat": 55.7, "lon": 37.6, "density": 4900},
        {"name": "Шанхай", "lat": 31.2, "lon": 121.5, "density": 7700},
    ]
    
    # Перевірка близькості до великих міст
    for city in major_cities:
        distance = calculate_distance(lat, lon, city["lat"], city["lon"])
        if distance < 50:  # В радіусі 50 км від міста
            decay_factor = max(0.1, 1 - (distance / 50))
            return {
                "area_type": "urban",
                "density": int(city["density"] * decay_factor),
                "nearest_city": city["name"],
                "distance_km": round(distance, 1)
            }
    
    # Базова оцінка по широті
    abs_lat = abs(lat)
    
    # Екватор - тропіки (висока густота в Азії/Африці)
    if abs_lat < 23.5:
        if 60 < lon < 150:  # Asia
            return {"area_type": "suburban", "density": 400, "nearest_city": "Region", "distance_km": 0}
        else:
            return {"area_type": "rural", "density": 80, "nearest_city": "Region", "distance_km": 0}
    
    # Temperate latitudes (more population in Europe/Asia)
    elif 23.5 <= abs_lat < 50:
        if -10 < lon < 50:  # Europe
            return {"area_type": "suburban", "density": 500, "nearest_city": "Europe", "distance_km": 0}
        elif 60 < lon < 150:  # Asia
            return {"area_type": "suburban", "density": 600, "nearest_city": "Asia", "distance_km": 0}
        elif -130 < lon < -60:  # North America
            return {"area_type": "suburban", "density": 200, "nearest_city": "America", "distance_km": 0}
        else:
            return {"area_type": "rural", "density": 50, "nearest_city": "Region", "distance_km": 0}
    
    # High latitudes (low population)
    else:
        return {"area_type": "rural", "density": 5, "nearest_city": "Remote region", "distance_km": 0}


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Відстань між двома точками (км)"""
    R = 6371  # Радіус Землі
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_casualties(airblast_zones: List[Dict], lat: float, lon: float) -> Dict:
    """Розрахунок людських втрат"""
    
    pop_info = estimate_population_density(lat, lon)
    base_density = pop_info["density"]
    
    casualties = {
        "total_deaths": 0,
        "total_injuries": 0,
        "affected_population": 0,
        "zones": []
    }
    
    for zone in airblast_zones:
        area_km2 = math.pi * (zone["radius_km"] ** 2)
        population = int(base_density * area_km2)
        
        # Коефіцієнти смертності залежно від зони
        if zone["type"] == "total_destruction":
            deaths = int(population * 0.95)
            injuries = int(population * 0.05)
        elif zone["type"] == "heavy_damage":
            deaths = int(population * 0.70)
            injuries = int(population * 0.25)
        elif zone["type"] == "moderate_damage":
            deaths = int(population * 0.25)
            injuries = int(population * 0.60)
        elif zone["type"] == "light_damage":
            deaths = int(population * 0.05)
            injuries = int(population * 0.50)
        elif zone["type"] == "glass_breakage":
            deaths = 0
            injuries = int(population * 0.15)
        else:
            deaths = 0
            injuries = 0
        
        casualties["total_deaths"] += deaths
        casualties["total_injuries"] += injuries
        casualties["affected_population"] += population
        
        casualties["zones"].append({
            "type": zone["type"],
            "radius_km": zone["radius_km"],
            "population": population,
            "deaths": deaths,
            "injuries": injuries
        })
    
    casualties["population_density"] = base_density
    casualties["area_type"] = pop_info["area_type"]
    casualties["nearest_city"] = pop_info["nearest_city"]
    
    return casualties


def calculate_economic_damage(airblast_zones: List[Dict], thermal_zones: List[Dict], lat: float, lon: float) -> Dict:
    """Розрахунок економічних збитків"""
    
    pop_info = estimate_population_density(lat, lon)
    
    # Визначення типу області для економічної оцінки
    if pop_info["density"] > 10000:
        infra_type = "megacity"
    elif pop_info["density"] > 3000:
        infra_type = "urban_dense"
    elif pop_info["density"] > 800:
        infra_type = "urban"
    elif pop_info["density"] > 200:
        infra_type = "suburban"
    else:
        infra_type = "rural"
    
    base_value = INFRASTRUCTURE_VALUE[infra_type]
    
    damage = {
        "total_damage_usd": 0,
        "by_type": {},
        "affected_area_km2": 0
    }
    
    # Збитки від ударної хвилі
    for zone in airblast_zones[:3]:  # Тільки перші 3 найсерйозніші зони
        area_km2 = math.pi * (zone["radius_km"] ** 2)
        
        if zone["type"] == "total_destruction":
            zone_damage = base_value * area_km2 * 1.0  # 100% знищення
        elif zone["type"] == "heavy_damage":
            zone_damage = base_value * area_km2 * 0.7  # 70% пошкодження
        elif zone["type"] == "moderate_damage":
            zone_damage = base_value * area_km2 * 0.4  # 40% пошкодження
        else:
            zone_damage = base_value * area_km2 * 0.1
        
        damage["total_damage_usd"] += zone_damage
        damage["affected_area_km2"] += area_km2
    
    # Додаткові збитки від пожеж (теплове випромінювання)
    if thermal_zones:
        fire_area = math.pi * (thermal_zones[0]["radius_km"] ** 2)
        fire_damage = base_value * fire_area * 0.3  # 30% додаткових збитків
        damage["total_damage_usd"] += fire_damage
        damage["by_type"]["fire_damage"] = fire_damage
    
    # Промислові об'єкти (якщо урбанізована зона)
    if infra_type in ["megacity", "urban_dense", "urban"]:
        industrial_multiplier = 1.5
        damage["total_damage_usd"] *= industrial_multiplier
        damage["by_type"]["industrial_factor"] = industrial_multiplier
    
    damage["total_damage_usd"] = int(damage["total_damage_usd"])
    damage["infrastructure_type"] = infra_type
    damage["damage_per_km2"] = int(base_value)
    
    return damage


def calculate_strategic_risks(lat: float, lon: float, radius_km: float) -> List[Dict]:
    """Оцінка ризиків для стратегічних об'єктів"""
    
    risks = []
    
    # Великі міста в радіусі
    pop_info = estimate_population_density(lat, lon)
    if pop_info["density"] > 3000:
        risks.append({
            "type": "major_city",
            "description": f"Велике місто ({pop_info.get('nearest_city', 'невідоме')}) в зоні ураження",
            "severity": "critical"
        })
    
    # Промислові зони
    if pop_info["density"] > 1000:
        risks.append({
            "type": "industrial",
            "description": "Ймовірність вторинних вибухів на підприємствах",
            "severity": "high"
        })
    
    # Ядерні об'єкти (спрощена оцінка по регіонах)
    nuclear_regions = [
        {"lat": 51.4, "lon": 30.1, "name": "Чорнобиль"},
        {"lat": 47.5, "lon": 34.6, "name": "Запоріжжя"},
    ]
    
    for nuc in nuclear_regions:
        dist = calculate_distance(lat, lon, nuc["lat"], nuc["lon"])
        if dist < radius_km:
            risks.append({
                "type": "nuclear",
                "description": f"АЕС {nuc['name']} в зоні ураження ({dist:.1f} км)",
                "severity": "critical"
            })
    
    return risks