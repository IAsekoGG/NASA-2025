// Головний файл - координація всіх модулів
import { initMap, changeMapStyle } from './map.js';
import { initImpactPanel } from './impact-panel.js';
//import { initScenariosPanel } from './scenarios-panel.js';
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

// Функція відкриття модального вікна
function openModal() {
  document.getElementById('articleModal').classList.remove('hidden');
}

// Функція закриття модального вікна
function closeModal() {
  document.getElementById('articleModal').classList.add('hidden');
}

// Обробник кнопки ✖
document.getElementById('closeModal').addEventListener('click', closeModal);

// Закриття при кліку поза модальним вікном
document.getElementById('articleModal').addEventListener('click', (event) => {
  if (event.target.id === 'articleModal') {
    closeModal();
  }
});

// Відкрити плашку результатів
function openResultsPanel() {
  document.getElementById('resultsPanel').classList.remove('hidden');
}

// Закрити плашку результатів
function closeResultsPanel() {
  document.getElementById('resultsPanel').classList.add('hidden');
}

// Обробник кнопки ✖
document.getElementById('closeResults').addEventListener('click', closeResultsPanel);