from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImpactRequest(BaseModel):
    lat: float
    lon: float
    size: float  # метри
    speed: float  # км/с
    angle: float  # градуси

FACTS = [
    "Тунгуський метеорит (1908) мав ~50м в діаметрі",
    "Динозаври вимерли від астероїда ~10км в діаметрі",
    "Метеорит 100м падає раз на ~10,000 років",
    "Температура в епіцентрі перевищує 10,000°C",
    "Метеорит швидкістю 20 км/с летить швидше за кулю в 60 разів"
]

@app.post("/impact")
def calculate_impact(req: ImpactRequest):
    # Проста фізична модель
    density = 3000  # кг/м³
    volume = (4/3) * math.pi * (req.size/2)**3
    mass = volume * density
    velocity = req.speed * 1000  # м/с
    
    # Кінетична енергія (Дж)
    energy_j = 0.5 * mass * velocity**2
    energy_mt = energy_j / (4.184 * 10**15)  # Мегатонни TNT
    
    # Перевірка чи в воді
    is_water = abs(req.lat) < 60 and random.random() > 0.3
    
    # Радіуси ефектів (км) - спрощена модель R ~ E^(1/3)
    energy_factor = energy_mt ** (1/3)
    
    crater_diameter = 0.1 * req.size * (req.speed/20)**0.5 / 1000
    airburst_radius = 0.3 * energy_factor
    thermal_radius = 0.5 * energy_factor
    seismic_radius = 0.8 * energy_factor
    
    layers = [
        {"type": "crater", "radius_km": crater_diameter/2, "color": "#888888"},
        {"type": "airburst", "radius_km": airburst_radius, "color": "#FF6B35"},
        {"type": "thermal", "radius_km": thermal_radius, "color": "#FFB627"},
        {"type": "seismic", "radius_km": seismic_radius, "color": "#00D9FF"}
    ]
    
    if is_water:
        tsunami_radius = 2.0 * energy_factor
        layers.append({"type": "tsunami", "radius_km": tsunami_radius, "color": "#0077BE"})
    
    # MMI шкала
    mmi = min(12, int(3 + math.log10(energy_mt + 1) * 2))
    
    return {
        "energy_Mt": round(energy_mt, 2),
        "crater_diameter_km": round(crater_diameter, 3),
        "mmi": mmi,
        "layers": layers,
        "fun_fact": random.choice(FACTS),
        "is_water": is_water
    }

@app.get("/")
def root():
    return {"status": "Asteroid Impact API працює ☄️"}

# Запуск: uvicorn main:app --reload