from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import math
import random

app = FastAPI(title="Asteroid Impact Simulator API")

# CORS - дозволені джерела
# Для продакшену додай свій домен
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend dev
    "http://127.0.0.1:3000",
    "file://",  # Якщо хтось відкриє напряму
    # "https://your-domain.com",  # Production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImpactRequest(BaseModel):
    lat: float
    lon: float
    size: float
    speed: float
    angle: float
    material: Optional[str] = "stone"
    scenario: Optional[str] = "ground"

FACTS = [
    "Тунгуський метеорит (1908) мав ~50м в діаметрі",
    "Динозаври вимерли від астероїда ~10км в діаметрі",
    "Метеорит 100м падає раз на ~10,000 років",
    "Температура в епіцентрі перевищує 10,000°C",
    "Метеорит швидкістю 20 км/с летить швидше за кулю в 60 разів",
    "Щодня на Землю падає близько 100 тонн космічного пилу",
    "Найбільший відомий кратер - Vredefort (300 км, ПАР)",
    "Астероїд Apophis пролетить близько до Землі у 2029 році"
]

# Властивості матеріалів
MATERIALS = {
    "stone": {"density": 3000, "strength": 1.0},
    "iron": {"density": 7800, "strength": 2.5},
    "ice": {"density": 917, "strength": 0.3}
}

@app.post("/impact")
def calculate_impact(req: ImpactRequest):
    # Властивості матеріалу
    mat = MATERIALS.get(req.material, MATERIALS["stone"])
    density = mat["density"]
    strength = mat["strength"]
    
    # Об'єм та маса
    volume = (4/3) * math.pi * (req.size/2)**3
    mass = volume * density
    velocity = req.speed * 1000
    
    # Енергія
    energy_j = 0.5 * mass * velocity**2
    energy_mt = energy_j / (4.184 * 10**15) * strength
    
    # Визначення сценарію
    is_water = abs(req.lat) < 60 and random.random() > 0.4
    scenario = req.scenario if req.scenario else ("water" if is_water else "ground")
    
    # Базові радіуси
    energy_factor = energy_mt ** (1/3)
    
    layers = []
    
    if scenario == "ground":
        # Падіння на землю
        crater_diameter = 0.1 * req.size * (req.speed/20)**0.5 / 1000
        layers = [
            {"type": "crater", "radius_km": crater_diameter/2, "color": "#888888"},
            {"type": "airburst", "radius_km": 0.3 * energy_factor, "color": "#FF6B35"},
            {"type": "thermal", "radius_km": 0.5 * energy_factor, "color": "#FFB627"},
            {"type": "seismic", "radius_km": 0.8 * energy_factor, "color": "#00D9FF"}
        ]
        
    elif scenario == "water":
        # Падіння у воду
        layers = [
            {"type": "crater", "radius_km": 0.05 * energy_factor, "color": "#888888"},
            {"type": "thermal", "radius_km": 0.4 * energy_factor, "color": "#FFB627"},
            {"type": "tsunami", "radius_km": 2.0 * energy_factor, "color": "#0077BE"}
        ]
        
    elif scenario == "airburst":
        # Вибух в атмосфері (без кратера)
        layers = [
            {"type": "airburst", "radius_km": 0.5 * energy_factor, "color": "#FF6B35"},
            {"type": "thermal", "radius_km": 0.7 * energy_factor, "color": "#FFB627"},
            {"type": "seismic", "radius_km": 0.4 * energy_factor, "color": "#00D9FF"}
        ]
        
    elif scenario == "fragmentation":
        # Розкол (кілька малих кратерів)
        base_radius = 0.15 * energy_factor
        layers = [
            {"type": "crater", "radius_km": base_radius, "color": "#888888"},
            {"type": "airburst", "radius_km": base_radius * 2, "color": "#FF6B35"},
            {"type": "thermal", "radius_km": base_radius * 3, "color": "#FFB627"}
        ]
    
    # MMI шкала
    mmi = min(12, int(3 + math.log10(energy_mt + 1) * 2))
    
    return {
        "energy_Mt": round(energy_mt, 2),
        "crater_diameter_km": layers[0]["radius_km"] * 2 if layers else 0,
        "mmi": mmi,
        "layers": layers,
        "fun_fact": random.choice(FACTS),
        "is_water": scenario == "water",
        "scenario": scenario
    }

@app.get("/")
def root():
    return {
        "status": "Asteroid Impact API працює ☄️",
        "version": "2.0 - Modular",
        "endpoints": ["/impact"]
    }