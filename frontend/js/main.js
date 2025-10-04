// Головний файл - координація всіх модулів
import { initMap, changeMapStyle } from './map.js';
import { initImpactPanel } from './impact-panel.js';
import { initScenariosPanel } from './scenarios-panel.js';
import { initResultsPanel } from './results-panel.js';
import { initArticles } from './articles.js';

// Глобальний стан додатку
window.APP_STATE = {
    map: null,
    selectedCoords: null,
    marker: null,
    currentImpact: null,
    savedImpacts: [],
    currentScenario: 'ground'
};

// Ініціалізація всього додатку
async function init() {
    console.log('🚀 Запуск Asteroid Impact Simulator...');
    
    // Ініціалізація мапи
    window.APP_STATE.map = initMap();
    
    // Ініціалізація панелей
    initImpactPanel();
    initScenariosPanel();
    initResultsPanel();
    
    // Ініціалізація статей
    initArticles();
    
    console.log('✅ Додаток готовий!');
}

// Запуск при завантаженні сторінки
document.addEventListener('DOMContentLoaded', init);