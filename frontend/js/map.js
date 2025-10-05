// Модуль мапи з реальними шарами густини населення
export function initMap() {
    const map = new maplibregl.Map({
        container: 'map',
        style: {
            version: 8,
            sources: {
                'osm': {
                    type: 'raster',
                    tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    attribution: '© OpenStreetMap'
                }
            },
            layers: [{
                id: 'osm-tiles',
                type: 'raster',
                source: 'osm'
            }]
        },
        center: [30.5, 50.45],
        zoom: 4
    });
    
    map.on('load', () => {
        addPopulationDensityLayer(map);
        addInfrastructureLayer(map);
    });
    
    addMapControls(map);
    addLegend(map);
    map.on('click', handleMapClick);
    
    return map;
}

function addPopulationDensityLayer(map) {
    // Реальний шар густини населення від CARTO
    map.addSource('population', {
        type: 'raster',
        tiles: [
            'https://api.mapbox.com/v4/mapbox.natural-earth-2/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'
        ],
        tileSize: 256
    });
    
    // Альтернативно - використати GHSL Population Grid
    map.addSource('ghsl-population', {
        type: 'raster',
        tiles: [
            'https://ghsl.jrc.ec.europa.eu/tiles/GHS_POP_GLOBE_R2019A/{z}/{x}/{y}.png'
        ],
        tileSize: 256,
        maxzoom: 14
    });
    
    map.addLayer({
        id: 'population-density',
        type: 'raster',
        source: 'ghsl-population',
        paint: {
            'raster-opacity': 0.6,
            'raster-hue-rotate': 0,
            'raster-brightness-min': 0,
            'raster-brightness-max': 1,
            'raster-contrast': 0.3,
            'raster-saturation': 0.5
        },
        layout: { visibility: 'none' }
    });
}

function addInfrastructureLayer(map) {
    // Об'єднаний шар: урбанізація + критична інфраструктура
    
    // Критичні об'єкти по всьому світу
    const criticalInfrastructure = [
        // Європа
        {coords: [30.29, 50.43], type: 'nuclear', name: 'Чорнобильська АЕС'},
        {coords: [34.58, 47.51], type: 'nuclear', name: 'Запорізька АЕС'},
        {coords: [2.17, 49.16], type: 'nuclear', name: 'Cattenom Nuclear'},
        {coords: [8.78, 49.96], type: 'nuclear', name: 'Biblis Nuclear'},
        
        // Азія
        {coords: [139.66, 35.73], type: 'nuclear', name: 'Fukushima Daiichi'},
        {coords: [129.39, 35.72], type: 'nuclear', name: 'Kori Nuclear'},
        {coords: [112.53, 30.62], type: 'nuclear', name: 'Three Gorges Dam'},
        
        // Америка
        {coords: [-77.79, 35.43], type: 'nuclear', name: 'Brunswick Nuclear'},
        {coords: [-118.56, 33.37], type: 'nuclear', name: 'San Onofre'},
        
        // Мегаполіси
        {coords: [139.69, 35.68], type: 'megacity', name: 'Токіо'},
        {coords: [-74.00, 40.71], type: 'megacity', name: 'Нью-Йорк'},
        {coords: [121.47, 31.23], type: 'megacity', name: 'Шанхай'},
        {coords: [77.21, 28.61], type: 'megacity', name: 'Делі'},
        {coords: [2.35, 48.85], type: 'megacity', name: 'Париж'},
        {coords: [-0.12, 51.50], type: 'megacity', name: 'Лондон'},
        {coords: [37.61, 55.75], type: 'megacity', name: 'Москва'},
    ];
    
    map.addSource('infrastructure', {
        type: 'geojson',
        data: {
            type: 'FeatureCollection',
            features: criticalInfrastructure.map(i => ({
                type: 'Feature',
                geometry: {type: 'Point', coordinates: i.coords},
                properties: {type: i.type, name: i.name}
            }))
        }
    });
    
    map.addLayer({
        id: 'infrastructure-points',
        type: 'circle',
        source: 'infrastructure',
        paint: {
            'circle-radius': [
                'match',
                ['get', 'type'],
                'nuclear', 7,
                'megacity', 9,
                6
            ],
            'circle-color': [
                'match',
                ['get', 'type'],
                'nuclear', '#FF0000',
                'megacity', '#FFD700',
                '#999999'
            ],
            'circle-stroke-width': 2,
            'circle-stroke-color': '#FFFFFF',
            'circle-opacity': 0.8
        },
        layout: { visibility: 'none' }
    });
    
    map.addLayer({
        id: 'infrastructure-labels',
        type: 'symbol',
        source: 'infrastructure',
        layout: {
            'text-field': ['get', 'name'],
            'text-size': 10,
            'text-offset': [0, 1.5],
            'text-anchor': 'top',
            visibility: 'none'
        },
        paint: {
            'text-color': '#000',
            'text-halo-color': '#FFF',
            'text-halo-width': 2
        }
    });
}

function addMapControls(map) {
    const controlsHTML = `
        <div class="map-controls">
            <button class="map-style-btn active" data-style="osm">Map</button>
            <button class="map-style-btn" data-style="satellite">Satellite</button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', controlsHTML);
    
    document.querySelectorAll('.map-style-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.map-style-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            changeMapStyle(map, btn.dataset.style);
        });
    });
    
    document.querySelectorAll('.layer-toggle input').forEach(input => {
        input.addEventListener('change', (e) => {
            toggleLayer(map, e.target.dataset.layer, e.target.checked);
        });
    });
}

export function changeMapStyle(map, style) {
    const styles = {
        'osm': {
            version: 8,
            sources: {
                'osm': {
                    type: 'raster',
                    tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                    tileSize: 256
                }
            },
            layers: [{id: 'osm-tiles', type: 'raster', source: 'osm'}]
        },
        'satellite': {
            version: 8,
            sources: {
                'satellite': {
                    type: 'raster',
                    tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
                    tileSize: 256
                }
            },
            layers: [{id: 'satellite-tiles', type: 'raster', source: 'satellite'}]
        }
    };
    
    map.setStyle(styles[style] || styles.osm);
    
    map.once('styledata', () => {
        addPopulationDensityLayer(map);
        addInfrastructureLayer(map);
    });
}

function toggleLayer(map, layerName, visible) {
    const visibility = visible ? 'visible' : 'none';
    
    if (layerName === 'population') {
        map.setLayoutProperty('population-density', 'visibility', visibility);
    } else if (layerName === 'infrastructure') {
        map.setLayoutProperty('infrastructure-points', 'visibility', visibility);
        map.setLayoutProperty('infrastructure-labels', 'visibility', visibility);
    }
}

function addLegend(map) {
    const legendHTML = `
        <div class="map-legend" id="mapLegend">
            <div style="font-weight: 600; margin-bottom: 12px;">🎯 Зони ураження</div>
            <div class="legend-item">
                <div class="legend-color" style="background: #000000;"></div>
                <div class="legend-label">Кратер</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #8B0000;"></div>
                <div class="legend-label">Повне знищення</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #DC143C;"></div>
                <div class="legend-label">Важкі руйнування</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF4500;"></div>
                <div class="legend-label">Середні руйнування</div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', legendHTML);
}

function handleMapClick(e) {
    window.APP_STATE.selectedCoords = e.lngLat;
    
    if (window.APP_STATE.marker) {
        window.APP_STATE.marker.remove();
    }
    
    window.APP_STATE.marker = new maplibregl.Marker({color: '#EF4444'})
        .setLngLat([e.lngLat.lng, e.lngLat.lat])
        .addTo(window.APP_STATE.map);
    
    const coordsEl = document.getElementById('selectedCoords');
    if (coordsEl) {
        coordsEl.textContent = `📍 ${e.lngLat.lat.toFixed(2)}°, ${e.lngLat.lng.toFixed(2)}°`;
    }
    
    const impactBtn = document.getElementById('impactBtn');
    if (impactBtn) {
        impactBtn.disabled = false;
    }
}

export function drawImpactEffects(layers) {
    const map = window.APP_STATE.map;
    const coords = window.APP_STATE.selectedCoords;
    
    removeAllImpactLayers(map);
    
    // Сортуємо: кратер -> сильні руйнування -> середні
    const orderedLayers = [];
    
    // Спочатку кратер
    const crater = layers.find(l => l.type === 'crater');
    if (crater) orderedLayers.push(crater);
    
    // Потім руйнування від найсильніших до слабких
    const damages = layers.filter(l => 
        l.type === 'total_destruction' || 
        l.type === 'heavy_damage' || 
        l.type === 'moderate_damage'
    ).sort((a, b) => b.radius_km - a.radius_km);
    
    orderedLayers.push(...damages);
    
    // Малюємо від найбільшого до найменшого
    orderedLayers.reverse().forEach((layer, index) => {
        const circle = createCircle(coords, layer.radius_km);
        const layerId = `impact_${layer.type}_${index}`;
        
        map.addSource(layerId, {
            type: 'geojson',
            data: circle
        });
        
        // Для кратера - чорний/сірий
        const fillColor = layer.type === 'crater' ? '#000000' : layer.color;
        const fillOpacity = layer.type === 'crater' ? 0.5 : 0.25;
        
        map.addLayer({
            id: layerId,
            type: 'fill',
            source: layerId,
            paint: {
                'fill-color': fillColor,
                'fill-opacity': fillOpacity
            }
        });
        
        map.addLayer({
            id: layerId + '_outline',
            type: 'line',
            source: layerId,
            paint: {
                'line-color': fillColor,
                'line-width': layer.type === 'crater' ? 3 : 2,
                'line-opacity': 0.8
            }
        });
    });
    
    //document.getElementById('mapLegend').style.display = 'block';
}

function removeAllImpactLayers(map) {
    const style = map.getStyle();
    if (!style || !style.layers) return;
    
    const layersToRemove = [];
    const sourcesToRemove = [];
    
    style.layers.forEach(layer => {
        if (layer.id.startsWith('impact_')) {
            layersToRemove.push(layer.id);
        }
    });
    
    if (style.sources) {
        Object.keys(style.sources).forEach(sourceId => {
            if (sourceId.startsWith('impact_')) {
                sourcesToRemove.push(sourceId);
            }
        });
    }
    
    layersToRemove.forEach(layerId => {
        if (map.getLayer(layerId)) {
            map.removeLayer(layerId);
        }
    });
    
    sourcesToRemove.forEach(sourceId => {
        if (map.getSource(sourceId)) {
            map.removeSource(sourceId);
        }
    });
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