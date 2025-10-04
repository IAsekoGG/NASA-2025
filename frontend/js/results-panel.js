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
    
    const labels = {
        crater: '🕳️ Кратер',
        airburst: '💥 Ударна хвиля',
        thermal: '🔥 Теплове випромінювання',
        seismic: '🌍 Землетрус',
        tsunami: '🌊 Цунамі'
    };
    
    const descriptions = {
        crater: 'Утворення ударного кратера',
        airburst: 'Вибиває вікна, руйнує будівлі',
        thermal: 'Займання, опіки',
        seismic: 'Коливання ґрунту',
        tsunami: 'Хвилі після падіння у воду'
    };
    
    let html = `
        <!-- Головна статистика -->
        <div class="p-4 bg-red-50 rounded-lg mb-4">
            <div class="text-2xl font-bold text-red-800">⚡ ${data.energy_Mt} Мегатонн</div>
            <div class="text-sm text-gray-600 mt-1">
                Енергія вибуху (${(data.energy_Mt * 1000).toFixed(0)} Хіросім)
            </div>
        </div>
        
        <div class="grid grid-cols-2 gap-3 mb-4">
            <div class="p-3 bg-gray-50 rounded">
                <div class="text-xs text-gray-600">Діаметр кратера</div>
                <div class="text-lg font-bold">${data.crater_diameter_km.toFixed(2)} км</div>
            </div>
            <div class="p-3 bg-gray-50 rounded">
                <div class="text-xs text-gray-600">Землетрус MMI</div>
                <div class="text-lg font-bold">${data.mmi}/12</div>
            </div>
        </div>
        
        <!-- Зони ураження -->
        <div class="mb-4">
            <div class="font-semibold mb-2">Зони ураження:</div>
    `;
    
    data.layers.forEach(layer => {
        html += `
            <div class="mb-2 p-3 rounded-lg" style="background-color: ${layer.color}22; border-left: 4px solid ${layer.color}">
                <div class="font-semibold">${labels[layer.type]}</div>
                <div class="text-sm text-gray-600">${descriptions[layer.type]}</div>
                <div class="text-sm font-bold mt-1">Радіус: ${layer.radius_km.toFixed(1)} км</div>
            </div>
        `;
    });
    
    html += `
        </div>
        
        <!-- Цікавий факт -->
        <div class="p-4 bg-blue-50 rounded-lg">
            <div class="text-sm font-semibold text-blue-800 mb-1">💡 Цікавий факт</div>
            <div class="text-sm text-gray-700">${data.fun_fact}</div>
        </div>
        
        <!-- Порівняння -->
        <div class="mt-4">
            <button class="btn btn-secondary w-full">Порівняти з історичними подіями</button>
        </div>
    `;
    
    content.innerHTML = html;
}