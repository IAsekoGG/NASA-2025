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
    
    result = {
        "energy": energy,
        "material": MATERIALS[req.material]["name"],
        "scenario": req.scenario,
        "fun_fact": random.choice(FACTS)
    }
    
    # Розрахунки залежно від сценарію
    if req.scenario == "ground":
        result["crater"] = calculate_crater(req.size, req.speed, req.angle, energy["energy_mt"])
        result["airblast"] = calculate_airblast(energy["energy_mt"])
        result["thermal"] = calculate_thermal(energy["energy_mt"])
        result["seismic"] = calculate_seismic(energy["energy_mt"])
        
        # Для мапи - всі зони
        result["layers"] = (
            [{"type": "crater", "radius_km": result["crater"]["diameter_km"]/2, "color": "#888888"}] +
            [{"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} for z in result["airblast"][:3]] +
            [{"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} for z in result["thermal"][:2]]
        )
        
    elif req.scenario == "water":
        result["tsunami"] = calculate_tsunami(energy["energy_mt"])
        result["thermal"] = calculate_thermal(energy["energy_mt"])
        result["airblast"] = calculate_airblast(energy["energy_mt"] * 0.5)  # Менша ударна хвиля у воді
        
        result["layers"] = (
            [{"type": "tsunami_" + str(i), "radius_km": z["distance_km"], "color": "#0077BE"} 
             for i, z in enumerate(result["tsunami"]["zones"][:3])] +
            [{"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} for z in result["thermal"][:2]]
        )
        
    elif req.scenario == "airburst":
        result["airburst_altitude_km"] = round(15 + random.uniform(-5, 10), 1)
        result["airblast"] = calculate_airblast(energy["energy_mt"])
        result["thermal"] = calculate_thermal(energy["energy_mt"], result["airburst_altitude_km"])
        result["seismic"] = calculate_seismic(energy["energy_mt"] * 0.3)
        
        result["layers"] = (
            [{"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} for z in result["airblast"][:4]] +
            [{"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} for z in result["thermal"][:2]]
        )
        
    elif req.scenario == "fragmentation":
        result["fragmentation"] = calculate_fragmentation(req.size, req.speed, req.material)
        # Об'єднані ефекти від усіх фрагментів
        result["airblast"] = calculate_airblast(energy["energy_mt"])
        
        result["layers"] = [
            {"type": z["type"], "radius_km": z["radius_km"], "color": z["color"]} 
            for z in result["airblast"][:3]
        ]
    
    return result


@app.get("/")
def root():
    """Кореневий endpoint - інформація про API"""
    return {
        "status": "Asteroid Impact API працює ☄️",
        "version": "3.0 - Advanced Physics",
        "features": ["Детальні зони ураження", "Цунамі розрахунки", "Медичні наслідки", "Сейсміка"]
    }