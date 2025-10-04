// Модуль мапи
export function initMap() {
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json',
        center: [30.5, 50.45],
        zoom: 4
    });
    
    // Додати контроли стилів
    addMapControls(map);
    
    // Додати легенду
    addLegend(map);
    
    // Обробка кліків
    map.on('click', handleMapClick);
    
    return map;
}

function addMapControls(map) {
    const controlsHTML = `
        <div class="map-controls">
            <button class="map-style-btn active" data-style="default">🌍 Стандарт</button>
            <button class="map-style-btn" data-style="dark">🌑 Темна</button>
            <button class="map-style-btn" data-style="satellite">🛰️ Супутник</button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', controlsHTML);
    
    // Обробка зміни стилю
    document.querySelectorAll('.map-style-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.map-style-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            changeMapStyle(map, btn.dataset.style);
        });
    });
}

export function changeMapStyle(map, style) {
    const styles = {
        'default': 'https://demotiles.maplibre.org/style.json',
        'dark': 'https://tiles.stadiamaps.com/styles/alidade_smooth_dark.json',
        'satellite': 'https://demotiles.maplibre.org/style.json' // можна додати інший
    };
    
    map.setStyle(styles[style] || styles.default);
}

function addLegend(map) {
    const legendHTML = `
        <div class="map-legend hidden" id="mapLegend">
            <div style="font-weight: 600; margin-bottom: 12px;">Ефекти удару</div>
            <div class="legend-item">
                <div class="legend-color" style="background: #888888;"></div>
                <div class="legend-label">🕳️ Кратер</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF6B35;"></div>
                <div class="legend-label">💥 Ударна хвиля</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFB627;"></div>
                <div class="legend-label">🔥 Теплове випромінювання</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #00D9FF;"></div>
                <div class="legend-label">🌍 Землетрус</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #0077BE;"></div>
                <div class="legend-label">🌊 Цунамі</div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', legendHTML);
}

function handleMapClick(e) {
    window.APP_STATE.selectedCoords = e.lngLat;
    
    // Видалити старий маркер
    if (window.APP_STATE.marker) {
        window.APP_STATE.marker.remove();
    }
    
    // Додати новий маркер
    window.APP_STATE.marker = new maplibregl.Marker({color: '#EF4444'})
        .setLngLat([e.lngLat.lng, e.lngLat.lat])
        .addTo(window.APP_STATE.map);
    
    // Оновити координати в панелі
    const coordsEl = document.getElementById('selectedCoords');
    if (coordsEl) {
        coordsEl.textContent = `📍 ${e.lngLat.lat.toFixed(2)}°, ${e.lngLat.lng.toFixed(2)}°`;
    }
    
    // Активувати кнопку удару
    const impactBtn = document.getElementById('impactBtn');
    if (impactBtn) {
        impactBtn.disabled = false;
    }
}

// Функція для малювання ефектів
export function drawImpactEffects(layers) {
    const map = window.APP_STATE.map;
    const coords = window.APP_STATE.selectedCoords;
    
    // Видалити старі шари
    ['crater', 'airburst', 'thermal', 'seismic', 'tsunami'].forEach(id => {
        if (map.getLayer(id)) map.removeLayer(id);
        if (map.getSource(id)) map.removeSource(id);
    });
    
    // Намалювати нові
    layers.forEach(layer => {
        const circle = createCircle(coords, layer.radius_km);
        
        map.addSource(layer.type, {
            type: 'geojson',
            data: circle
        });
        
        map.addLayer({
            id: layer.type,
            type: 'fill',
            source: layer.type,
            paint: {
                'fill-color': layer.color,
                'fill-opacity': 0.3,
                'fill-outline-color': layer.color
            }
        });
    });
    
    // Показати легенду
    document.getElementById('mapLegend').classList.remove('hidden');
}

function createCircle(center, radiusKm, points = 64) {
    const coords = [];
    const distanceX = radiusKm / (111.32 * Math.cos(center.lat * Math.PI / 180));
    const distanceY = radiusKm / 110.574;

    for (let i = 0; i < points; i++) {
        const theta = (i / points) * (2 * Math.PI);
        const x = distanceX * Math.cos(theta);
        const y = distanceY * Math.sin(theta);
        coords.push([center.lng + x, center.lat + y]);
    }
    coords.push(coords[0]);

    return {
        type: 'Feature',
        geometry: {
            type: 'Polygon',
            coordinates: [coords]
        }
    };
}