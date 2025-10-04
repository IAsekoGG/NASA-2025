from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

from models import ImpactRequest
from constants import MATERIALS, FACTS
from calculations import (
    calculate_energy,
    calculate_crater,
    calculate_airblast,
    calculate_thermal,
    calculate_seismic,
    calculate_tsunami,
    calculate_fragmentation
)
from casualties import (
    calculate_casualties,
    calculate_economic_damage,
    calculate_strategic_risks,
    estimate_population_density
)

app = FastAPI(title="Asteroid Impact Simulator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/impact")
def calculate_impact(req: ImpactRequest):
    """Головний endpoint для розрахунку наслідків удару астероїда"""
    
    # Базова енергія
    energy = calculate_energy(req.size, req.speed, req.material)
    
    # Інформація про населення
    pop_info = estimate_population_density(req.lat, req.lon)
    
    # Отримуємо густину матеріалу з constants
    material_density = MATERIALS[req.material]["density"]
    
    result = {
        "energy": energy,
        "material": MATERIALS[req.material]["name"],
        "scenario": req.scenario,
        "fun_fact": random.choice(FACTS),
        "location": pop_info
    }
    
    # Розрахунки залежно від сценарію
    if req.scenario == "ground":
        # ВИПРАВЛЕНО: передаємо густину матеріалу замість енергії
        result["crater"] = calculate_crater(
            req.size,           # діаметр метеорита (м)
            req.speed,          # швидкість (км/с)
            req.angle,          # кут падіння (градуси)
            material_density    # густина матеріалу (кг/м³) - 3000 для stone, 7800 для iron, 917 для ice
        )
        
        result["airblast"] = calculate_airblast(energy["energy_mt"])
        result["thermal"] = calculate_thermal(energy["energy_mt"])
        result["seismic"] = calculate_seismic(energy["energy_mt"])
        
        # Втрати та збитки тільки для наземного удару
        result["casualties"] = calculate_casualties(result["airblast"], req.lat, req.lon)
        result["economic_damage"] = calculate_economic_damage(
            result["airblast"], 
            result["thermal"], 
            req.lat, 
            req.lon
        )
        result["strategic_risks"] = calculate_strategic_risks(
            req.lat, 
            req.lon, 
            result["airblast"][0]["radius_km"]
        )
        
        # Для мапи: кратер -> сильні руйнування -> середні
        result["layers"] = (
            [{"type": "crater", "radius_km": result["crater"]["diameter_km"]/2, "color": "#000000"}] +
            [{"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} 
             for z in result["airblast"] 
             if z["type"] in ["total_destruction", "heavy_damage", "moderate_damage"]]
        )
        
    elif req.scenario == "water":
        result["tsunami"] = calculate_tsunami(energy["energy_mt"])
        result["thermal"] = calculate_thermal(energy["energy_mt"])
        result["airblast"] = calculate_airblast(energy["energy_mt"] * 0.5)
        
        # Для води НЕ рахуємо casualties та economic_damage - нелогічно
        
        result["layers"] = (
            [{"type": "tsunami_" + str(i), "radius_km": z["distance_km"], "color": "#0077BE"} 
             for i, z in enumerate(result["tsunami"]["zones"][:3])]
        )
        
    elif req.scenario == "airburst":
        result["airburst_altitude_km"] = round(15 + random.uniform(-5, 10), 1)
        result["airblast"] = calculate_airblast(energy["energy_mt"])
        result["thermal"] = calculate_thermal(energy["energy_mt"], result["airburst_altitude_km"])
        result["seismic"] = calculate_seismic(energy["energy_mt"] * 0.3)
        
        # Втрати та збитки для airburst
        result["casualties"] = calculate_casualties(result["airblast"], req.lat, req.lon)
        result["economic_damage"] = calculate_economic_damage(
            result["airblast"], 
            result["thermal"], 
            req.lat, 
            req.lon
        )
        
        # Для мапи: руйнування без кратера
        result["layers"] = [
            {"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} 
            for z in result["airblast"] 
            if z["type"] in ["total_destruction", "heavy_damage", "moderate_damage"]
        ]
        
    elif req.scenario == "fragmentation":
        result["fragmentation"] = calculate_fragmentation(req.size, req.speed, req.material)
        result["airblast"] = calculate_airblast(energy["energy_mt"])
        
        # Втрати та збитки для fragmentation
        result["casualties"] = calculate_casualties(result["airblast"], req.lat, req.lon)
        result["economic_damage"] = calculate_economic_damage(
            result["airblast"], 
            [], 
            req.lat, 
            req.lon
        )
        
        result["layers"] = [
            {"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} 
            for z in result["airblast"]
            if z["type"] in ["total_destruction", "heavy_damage", "moderate_damage"]
        ]
    
    return result


@app.get("/")
def root():
    """Кореневий endpoint - інформація про API"""
    return {
        "status": "Asteroid Impact API працює ☄️",
        "version": "3.1 - Population & Economics",
        "features": [
            "Детальні зони ураження",
            "Цунамі розрахунки",
            "Оцінка людських втрат",
            "Економічні збитки",
            "Стратегічні ризики"
        ]
    }