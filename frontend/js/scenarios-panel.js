// Модуль панелі "Сценарії"
import { openArticle } from './articles.js';

export function initScenariosPanel() {
    const panel = document.getElementById('scenariosPanel');
    
    panel.innerHTML = `
        <div class="panel-header">
            <div class="panel-title">🎭 Сценарії падіння</div>
        </div>
        
        <div class="panel-body">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div class="card" data-scenario="water" onclick="selectScenario('water')">
                    <div class="card-title">
                        🌊 У воду
                        <button class="btn-info" onclick="event.stopPropagation(); openArticle('water-impact')">ℹ️</button>
                    </div>
                    <div class="card-description">Цунамі, парові викиди</div>
                </div>
                
                <div class="card selected" data-scenario="ground" onclick="selectScenario('ground')">
                    <div class="card-title">
                        🏔️ На землю
                        <button class="btn-info" onclick="event.stopPropagation(); openArticle('ground-impact')">ℹ️</button>
                    </div>
                    <div class="card-description">Кратер, ударна хвиля</div>
                </div>
                
                <div class="card" data-scenario="airburst" onclick="selectScenario('airburst')">
                    <div class="card-title">
                        💥 Вибух в атмосфері
                        <button class="btn-info" onclick="event.stopPropagation(); openArticle('airburst')">ℹ️</button>
                    </div>
                    <div class="card-description">Без кратера, велика хвиля</div>
                </div>
                
                <div class="card" data-scenario="fragmentation" onclick="selectScenario('fragmentation')">
                    <div class="card-title">🧩 Розкол</div>
                    <div class="card-description">Кілька малих ударів</div>
                </div>
            </div>
            
            <!-- Додаткові параметри сценарію -->
            <div id="scenarioParams" class="mt-4"></div>
        </div>
    `;
    
    // Ініціалізувати початковий сценарій
    setTimeout(() => showScenarioParams('ground'), 100);
}

window.selectScenario = function(scenario) {
    // Знайти картку по data-scenario
    const cards = document.querySelectorAll('#scenariosPanel .card');
    
    // Зняти виділення з усіх
    cards.forEach(c => c.classList.remove('selected'));
    
    // Виділити вибрану
    const selectedCard = document.querySelector(`#scenariosPanel .card[data-scenario="${scenario}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    // Оновити глобальний стан
    window.APP_STATE.currentScenario = scenario;
    
    console.log('🎭 Обрано сценарій:', scenario);
    
    // Показати додаткові параметри
    showScenarioParams(scenario);
};

function showScenarioParams(scenario) {
    const paramsDiv = document.getElementById('scenarioParams');
    
    const params = {
        water: `
            <div class="p-4 bg-blue-50 rounded-lg">
                <div class="font-semibold mb-2">Параметри падіння у воду:</div>
                <div class="input-group">
                    <label class="input-label">Глибина океану (м)</label>
                    <input type="range" id="waterDepth" min="100" max="5000" value="2000" class="input-range">
                    <span id="waterDepthValue" class="input-value">2000 м</span>
                </div>
            </div>
        `,
        ground: `
            <div class="p-4 bg-amber-50 rounded-lg">
                <div class="font-semibold mb-2">Параметри падіння на землю:</div>
                <div class="input-group">
                    <label class="input-label">Тип ґрунту</label>
                    <select id="groundType" class="w-full p-2 border rounded">
                        <option value="rock">🪨 Скеляста порода</option>
                        <option value="sand">🏖️ Пісок</option>
                        <option value="soil">🌱 Ґрунт</option>
                    </select>
                </div>
            </div>
        `,
        airburst: `
            <div class="p-4 bg-orange-50 rounded-lg">
                <div class="font-semibold mb-2">Вибух в атмосфері:</div>
                <div class="input-group">
                    <label class="input-label">Висота вибуху (км)</label>
                    <input type="range" id="burstAlt" min="5" max="50" value="15" class="input-range">
                    <span id="burstAltValue" class="input-value">15 км</span>
                </div>
            </div>
        `,
        fragmentation: `
            <div class="p-4 bg-purple-50 rounded-lg">
                <div class="font-semibold mb-2">Розкол на шматки:</div>
                <div class="input-group">
                    <label class="input-label">Кількість фрагментів</label>
                    <input type="range" id="fragments" min="2" max="10" value="3" class="input-range">
                    <span id="fragmentsValue" class="input-value">3 шт</span>
                </div>
            </div>
        `
    };
    
    paramsDiv.innerHTML = params[scenario] || '';
    
    // Додати обробники для нових слайдерів
    const sliders = paramsDiv.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        slider.oninput = (e) => {
            const valueEl = document.getElementById(e.target.id + 'Value');
            if (valueEl) {
                const unit = valueEl.textContent.split(' ')[1];
                valueEl.textContent = e.target.value + ' ' + unit;
            }
        };
    });

    showScenarioParams('ground');
}

window.openArticle = openArticle;