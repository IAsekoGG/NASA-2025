// Модуль панелі "Наслідки"
export function initResultsPanel() {
    const panel = document.getElementById('resultsPanel');
    
    panel.innerHTML = `
        <div class="panel-header">
            <div class="panel-title">📊 Наслідки удару</div>
        </div>
        <div class="panel-body" id="resultsContent"></div>
    `;
}

export function showResults(data) {
    const panel = document.getElementById('resultsPanel');
    const content = document.getElementById('resultsContent');
    
    panel.classList.remove('hidden');
    
    let html = '';
    
    // Загальна енергія
    html += `
        <div class="p-4 bg-red-50 rounded-lg mb-4 border-2 border-red-200">
            <div class="text-3xl font-bold text-red-800">⚡ ${data.energy.energy_mt} Мегатонн</div>
            <div class="text-sm text-gray-700 mt-2">
                <div>💣 ${data.energy.hiroshima_eq} × Хіросіма</div>
                <div>🧨 ${(data.energy.tnt_kg / 1e6).toFixed(1)} млн кг TNT</div>
                <div>⚙️ Матеріал: ${data.material}</div>
            </div>
        </div>
    `;
    
    // Залежно від сценарію
    if (data.scenario === 'ground') {
        html += renderGroundImpact(data);
    } else if (data.scenario === 'water') {
        html += renderWaterImpact(data);
    } else if (data.scenario === 'airburst') {
        html += renderAirburst(data);
    } else if (data.scenario === 'fragmentation') {
        html += renderFragmentation(data);
    }
    
    // Цікавий факт
    html += `
        <div class="mt-4 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
            <div class="text-sm font-semibold text-blue-800 mb-1">💡 Цікавий факт</div>
            <div class="text-sm text-gray-700">${data.fun_fact}</div>
        </div>
    `;
    
    content.innerHTML = html;
}

function renderGroundImpact(data) {
    let html = '';
    
    // Кратер
    html += `
        <div class="mb-4">
            <h3 class="font-bold text-lg mb-2">🕳️ Кратер</h3>
            <div class="grid grid-cols-2 gap-2">
                <div class="p-3 bg-gray-100 rounded">
                    <div class="text-xs text-gray-600">Діаметр</div>
                    <div class="text-lg font-bold">${data.crater.diameter_km} км</div>
                </div>
                <div class="p-3 bg-gray-100 rounded">
                    <div class="text-xs text-gray-600">Глибина</div>
                    <div class="text-lg font-bold">${data.crater.depth_km} км</div>
                </div>
            </div>
            <div class="text-xs text-gray-600 mt-2">
                Викинута порода: ${(data.crater.ejecta_mass_kg / 1e9).toFixed(1)} млрд кг
            </div>
        </div>
    `;
    
    // Ударна хвиля
    html += `
        <div class="mb-4">
            <h3 class="font-bold text-lg mb-2">💥 Ударна хвиля</h3>
    `;
    
    data.airblast.slice(0, 4).forEach(zone => {
        html += `
            <div class="mb-2 p-3 rounded-lg border-l-4" style="background-color: ${zone.color}22; border-color: ${zone.color}">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="font-semibold text-sm">${zone.effects}</div>
                        <div class="text-xs text-red-700 font-medium mt-1">${zone.casualties}</div>
                        <div class="text-xs text-gray-600 mt-1">Тиск: ${zone.pressure_kpa} кПа</div>
                    </div>
                    <div class="text-right">
                        <div class="font-bold text-lg">${zone.radius_km} км</div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    // Теплове випромінювання
    html += `
        <div class="mb-4">
            <h3 class="font-bold text-lg mb-2">🔥 Теплове випромінювання</h3>
    `;
    
    data.thermal.forEach(zone => {
        html += `
            <div class="mb-2 p-3 rounded-lg border-l-4" style="background-color: ${zone.color}22; border-color: ${zone.color}">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="font-semibold text-sm">${zone.effects}</div>
                        <div class="text-xs text-red-700 font-medium mt-1">${zone.casualties}</div>
                        <div class="text-xs text-gray-600 mt-1">${zone.ignition}</div>
                    </div>
                    <div class="text-right">
                        <div class="font-bold text-lg">${zone.radius_km} км</div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    // Сейсміка
    if (data.seismic && data.seismic.length > 0) {
        const maxMmi = data.seismic[0];
        html += `
            <div class="mb-4">
                <h3 class="font-bold text-lg mb-2">🌍 Землетрус</h3>
                <div class="p-3 bg-purple-50 rounded-lg border-2 border-purple-200">
                    <div class="text-sm">
                        <div class="font-bold">Магнітуда: ${maxMmi.magnitude_richter} за Рихтером</div>
                        <div class="text-xs text-gray-600 mt-1">Максимальна інтенсивність: MMI ${maxMmi.mmi}</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    return html;
}

function renderWaterImpact(data) {
    let html = '';
    
    // Цунамі
    html += `
        <div class="mb-4">
            <h3 class="font-bold text-lg mb-2">🌊 Цунамі</h3>
            <div class="p-3 bg-blue-50 rounded-lg border-2 border-blue-200 mb-3">
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <div class="text-xs text-gray-600">Швидкість</div>
                        <div class="font-bold">${data.tsunami.wave_speed_kmh} км/год</div>
                    </div>
                    <div>
                        <div class="text-xs text-gray-600">Початкова висота</div>
                        <div class="font-bold">${data.tsunami.initial_height_m} м</div>
                    </div>
                </div>
            </div>
            
            <div class="text-xs font-semibold mb-2">Прибуття хвиль на різні відстані:</div>
            <div class="space-y-2">
    `;
    
    data.tsunami.zones.forEach(zone => {
        html += `
            <div class="p-2 bg-blue-50 rounded border-l-4 border-blue-400">
                <div class="flex justify-between text-sm">
                    <span class="font-semibold">${zone.distance_km} км</span>
                    <span class="text-blue-700">${zone.wave_height_m} м висота</span>
                </div>
                <div class="text-xs text-gray-600 mt-1">
                    Час прибуття: ${zone.arrival_time_min} хв | Run-up: ${zone.runup_m} м
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
            <div class="mt-2 p-2 bg-yellow-50 rounded text-xs">
                ⚠️ Час для евакуації: ${data.tsunami.warning_time_min} хвилин
            </div>
        </div>
    `;
    
    // Теплове випромінювання
    if (data.thermal) {
        html += `
            <div class="mb-4">
                <h3 class="font-bold text-lg mb-2">🔥 Теплове випромінювання</h3>
        `;
        
        data.thermal.slice(0, 2).forEach(zone => {
            html += `
                <div class="mb-2 p-2 rounded border-l-4" style="background-color: ${zone.color}22; border-color: ${zone.color}">
                    <div class="text-sm font-semibold">${zone.effects}</div>
                    <div class="text-xs text-gray-600">Радіус: ${zone.radius_km} км</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    return html;
}

function renderAirburst(data) {
    let html = '';
    
    html += `
        <div class="p-3 bg-orange-50 rounded-lg border-2 border-orange-200 mb-4">
            <div class="font-bold text-sm">💥 Вибух в атмосфері</div>
            <div class="text-xs text-gray-600 mt-1">
                Висота детонації: ${data.airburst_altitude_km} км
            </div>
            <div class="text-xs text-gray-500 mt-1">
                Без утворення кратера, але потужна ударна хвиля
            </div>
        </div>
    `;
    
    // Ударна хвиля
    html += `
        <div class="mb-4">
            <h3 class="font-bold text-lg mb-2">💥 Ударна хвиля</h3>
    `;
    
    data.airblast.slice(0, 5).forEach(zone => {
        html += `
            <div class="mb-2 p-3 rounded-lg border-l-4" style="background-color: ${zone.color}22; border-color: ${zone.color}">
                <div class="flex justify-between">
                    <div class="flex-1">
                        <div class="font-semibold text-sm">${zone.effects}</div>
                        <div class="text-xs text-red-700 mt-1">${zone.casualties}</div>
                    </div>
                    <div class="font-bold text-lg">${zone.radius_km} км</div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    // Теплове
    if (data.thermal) {
        html += '<div class="mb-4"><h3 class="font-bold text-lg mb-2">🔥 Теплове випромінювання</h3>';
        data.thermal.slice(0, 2).forEach(zone => {
            html += `
                <div class="mb-2 p-2 rounded border-l-4" style="background-color: ${zone.color}22; border-color: ${zone.color}">
                    <div class="text-sm font-semibold">${zone.effects}</div>
                    <div class="text-xs">Радіус: ${zone.radius_km} км</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    return html;
}

function renderFragmentation(data) {
    let html = '';
    
    html += `
        <div class="p-3 bg-purple-50 rounded-lg border-2 border-purple-200 mb-4">
            <div class="font-bold text-sm">🧩 Розкол на фрагменти</div>
            <div class="text-xs text-gray-600 mt-1">
                Висота розпаду: ${data.fragmentation.fragmentation_altitude_km} км
            </div>
            <div class="text-xs text-gray-600">
                Загальна енергія: ${data.fragmentation.total_energy_mt} Мт
            </div>
        </div>
    `;
    
    html += '<div class="mb-4"><h3 class="font-bold text-lg mb-2">💎 Фрагменти</h3>';
    
    data.fragmentation.fragments.forEach(frag => {
        html += `
            <div class="mb-3 p-3 bg-gray-50 rounded-lg border-2 border-gray-300">
                <div class="flex justify-between items-start mb-2">
                    <div class="font-bold text-sm">Фрагмент #${frag.id}</div>
                    <div class="text-xs bg-red-100 px-2 py-1 rounded">${frag.energy_mt} Мт</div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <div>
                        <div class="text-gray-600">Розмір</div>
                        <div class="font-semibold">${frag.size_m} м</div>
                    </div>
                    <div>
                        <div class="text-gray-600">Радіус вибуху</div>
                        <div class="font-semibold">${frag.blast_radius_km} км</div>
                    </div>
                </div>
                <div class="text-xs text-gray-500 mt-1">
                    Відстань між ударами: ${frag.separation_km} км
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Загальна ударна хвиля
    if (data.airblast) {
        html += '<div class="mb-4"><h3 class="font-bold text-lg mb-2">💥 Сумарна ударна хвиля</h3>';
        data.airblast.slice(0, 3).forEach(zone => {
            html += `
                <div class="mb-2 p-2 rounded border-l-4" style="background-color: ${zone.color}22; border-color: ${zone.color}">
                    <div class="text-sm">${zone.effects}</div>
                    <div class="text-xs">Радіус: ${zone.radius_km} км</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    return html;
}