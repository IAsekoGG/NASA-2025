// Модуль панелі "Врони метеорит"
import { callImpactAPI } from './api.js';
import { drawImpactEffects } from './map.js';
import { showResults } from './results-panel.js';
import { openArticle } from './articles.js';

export function initImpactPanel() {
    const panel = document.getElementById('impactPanel');
    
    panel.innerHTML = `
        <div class="panel-header">
            <div class="panel-title">
                ☄️ Врони метеорит
                <button class="btn-info" onclick="openArticle('asteroid-basics')">ℹ️</button>
            </div>
        </div>
        
        <div class="panel-body">
            <!-- Вкладки -->
            <div class="tabs">
                <div class="tab active" data-tab="params">Параметри</div>
                <div class="tab" data-tab="saved">Збережені</div>
            </div>
            
            <!-- Вкладка: Параметри -->
            <div class="tab-content active" id="tab-params">
                <div id="selectedCoords" class="text-sm text-gray-500 mb-4">📍 Натисни на мапу</div>
                
                <div class="input-group">
                    <label class="input-label">
                        Розмір (м)
                        <button class="btn-info" onclick="openArticle('impact-effects')">ℹ️</button>
                    </label>
                    <input type="range" id="size" min="10" max="1000" value="100" class="input-range">
                    <span id="sizeValue" class="input-value">100 м</span>
                </div>
                
                <div class="input-group">
                    <label class="input-label">Швидкість (км/с)</label>
                    <input type="range" id="speed" min="5" max="70" value="20" class="input-range">
                    <span id="speedValue" class="input-value">20 км/с</span>
                </div>
                
                <div class="input-group">
                    <label class="input-label">Кут падіння (°)</label>
                    <input type="range" id="angle" min="10" max="90" value="45" class="input-range">
                    <span id="angleValue" class="input-value">45°</span>
                </div>
                
                <div class="input-group">
                    <label class="input-label">Матеріал</label>
                    <select id="material" class="w-full p-2 border rounded">
                        <option value="stone">🪨 Кам'яний</option>
                        <option value="iron">⚙️ Залізний</option>
                        <option value="ice">🧊 Льодяний</option>
                    </select>
                </div>
                
                <button id="impactBtn" class="btn btn-primary w-full" disabled>
                    ВРОНИ МЕТЕОРИТ 💥
                </button>
            </div>
            
            <!-- Вкладка: Збережені -->
            <div class="tab-content" id="tab-saved">
                <div id="savedList">Немає збережених симуляцій</div>
            </div>
        </div>
    `;
    
    // Обробники подій
    setupEventListeners();
}

function setupEventListeners() {
    // Вкладки
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
        });
    });
    
    // Слайдери
    document.getElementById('size').oninput = (e) => {
        document.getElementById('sizeValue').textContent = e.target.value + ' м';
    };
    
    document.getElementById('speed').oninput = (e) => {
        document.getElementById('speedValue').textContent = e.target.value + ' км/с';
    };
    
    document.getElementById('angle').oninput = (e) => {
        document.getElementById('angleValue').textContent = e.target.value + '°';
    };
    
    // Кнопка удару
    document.getElementById('impactBtn').addEventListener('click', handleImpact);
}

async function handleImpact() {
    if (!window.APP_STATE.selectedCoords) return;
    
    const params = {
        lat: window.APP_STATE.selectedCoords.lat,
        lon: window.APP_STATE.selectedCoords.lng,
        size: parseFloat(document.getElementById('size').value),
        speed: parseFloat(document.getElementById('speed').value),
        angle: parseFloat(document.getElementById('angle').value),
        material: document.getElementById('material').value,
        scenario: window.APP_STATE.currentScenario || 'ground'  // Додано!
    };
    
    try {
        const result = await callImpactAPI(params);
        
        // Зберегти результат
        window.APP_STATE.currentImpact = result;
        saveImpact(params, result);
        
        // Намалювати на мапі
        drawImpactEffects(result.layers);
        
        // Показати результати
        showResults(result);
        
    } catch (err) {
        alert('Помилка: ' + err.message);
    }
}

function saveImpact(params, result) {
    const impact = {
        id: Date.now(),
        date: new Date().toLocaleString('uk-UA'),
        params,
        result
    };
    
    window.APP_STATE.savedImpacts.unshift(impact);
    updateSavedList();
}

function updateSavedList() {
    const list = document.getElementById('savedList');
    
    if (window.APP_STATE.savedImpacts.length === 0) {
        list.innerHTML = '<p class="text-gray-500">Немає збережених симуляцій</p>';
        return;
    }
    
    list.innerHTML = window.APP_STATE.savedImpacts.map(impact => `
        <div class="card" onclick="loadImpact(${impact.id})">
            <div class="card-title">${impact.params.size}м @ ${impact.params.speed}км/с</div>
            <div class="card-description">
                ${impact.result.energy_Mt} Мт • ${impact.date}
            </div>
        </div>
    `).join('');
}

window.loadImpact = function(id) {
    const impact = window.APP_STATE.savedImpacts.find(i => i.id === id);
    if (!impact) return;
    
    // Відновити параметри
    document.getElementById('size').value = impact.params.size;
    document.getElementById('speed').value = impact.params.speed;
    document.getElementById('angle').value = impact.params.angle;
    
    // Оновити відображення
    document.getElementById('sizeValue').textContent = impact.params.size + ' м';
    document.getElementById('speedValue').textContent = impact.params.speed + ' км/с';
    document.getElementById('angleValue').textContent = impact.params.angle + '°';
    
    // Показати результати
    window.APP_STATE.currentImpact = impact.result;
    drawImpactEffects(impact.result.layers);
    showResults(impact.result);
};

// Експорт для використання в HTML
window.openArticle = openArticle;