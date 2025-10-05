// Модуль панелі "Врони метеорит"
import { callImpactAPI } from './api.js';
import { drawImpactEffects } from './map.js';
import { showResults } from './results-panel.js';
import { openArticle } from './articles.js';

// 10 готових пресетів для вкладки "Збережені" (без челябінська, для симуляції)
const PRESET_METEORS = [
  // Реальні падіння / історичні
  { id: 'hoba', title: 'Hoba', sub: 'Намібія, залізний', params: { size: 1000, speed: 12, angle: 20, material: 'iron' }, info: 'Найбільший знайдений метеорит (м’яке приземлення).' },
  { id: 'allende', title: 'Allende', sub: 'Мексика, кам’яний', params: { size: 200, speed: 17, angle: 35, material: 'stone' }, info: 'CV3 хондрит, багатий на ранні сонячні конденсати.' },
  { id: 'murchison', title: 'Murchison', sub: 'Австралія, кам’яний', params: { size: 150, speed: 16, angle: 40, material: 'stone' }, info: 'CM2 хондрит, органіка та амінокислоти.' },
  { id: 'ensisheim', title: 'Ensisheim', sub: 'Франція, 1492', params: { size: 120, speed: 15, angle: 45, material: 'stone' }, info: 'Класичний історичний хондрит.' },
  { id: 'diablo', title: 'Meteor Crater body', sub: 'США, залізний', params: { size: 50, speed: 15, angle: 45, material: 'iron' }, info: 'Попередник кратера Баррінджера (оцінкові параметри).' },
  { id: 'peekskill', title: 'Peekskill', sub: 'США, 1992', params: { size: 10, speed: 15, angle: 55, material: 'stone' }, info: 'Відоме падіння, зафіксоване на відео.' },

  // Глобальні катастрофи / симуляції
  { id: 'chicxulub', title: 'Chicxulub Impactor', sub: '66 млн років тому', params: { size: 10000, speed: 20, angle: 45, material: 'stone' }, info: '≈10 км астероїд, що спричинив масове вимирання динозаврів.' },

  // Близькі прольоти — змодельовані як гіпотетичне падіння
  { id: 'apophis2029', title: '99942 Apophis', sub: '13 квітня 2029', params: { size: 340, speed: 7.4, angle: 45, material: 'stone' }, info: 'Реально пролетить безпечно; тут — гіпотетичний удар.' },
  { id: 'duende2013', title: '2012 DA14 (Duende)', sub: '15 лютого 2013', params: { size: 50, speed: 7.8, angle: 45, material: 'stone' }, info: 'Низький проліт; тут — як симульований удар.' },
  { id: '2019ok', title: '2019 OK', sub: '25 липня 2019', params: { size: 120, speed: 24.6, angle: 45, material: 'stone' }, info: '“Зненацька” зближення; гіпотетичний удар.' },
  { id: '2020qg', title: '2020 QG', sub: '16 серпня 2020', params: { size: 5, speed: 12.3, angle: 60, material: 'stone' }, info: 'Дуже близький проліт; симуляція дрібного боліда.' }
];

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
          <label class="input-label">
            Швидкість (км/с)
            <button class="btn-info" onclick="openArticle('speed')">ℹ️</button>
          </label>
          <input type="range" id="speed" min="5" max="70" value="20" class="input-range">
          <span id="speedValue" class="input-value">20 км/с</span>
        </div>

        <div class="input-group">
          <label class="input-label">Кут падіння (°)</label>
          <input type="range" id="angle" min="10" max="90" value="45" class="input-range">
          <span id="angleValue" class="input-value">45°</span>
        </div>

        <div class="input-group">
          <label class="input-label">
            Матеріал
            <button class="btn-info" onclick="openArticle('materials')">ℹ️</button>
          </label>
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
        <div id="savedList" class="grid gap-2"></div>
      </div>
    </div>
  `;

  setupEventListeners();
  renderSavedPresets();
}

// Вкладки та інпути
function setupEventListeners() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
    });
  });

  document.getElementById('size').oninput = e => {
    document.getElementById('sizeValue').textContent = e.target.value + ' м';
  };
  document.getElementById('speed').oninput = e => {
    document.getElementById('speedValue').textContent = e.target.value + ' км/с';
  };
  document.getElementById('angle').oninput = e => {
    document.getElementById('angleValue').textContent = e.target.value + '°';
  };

  // Виклик користувацького удару (без збереження історії)
  document.getElementById('impactBtn').addEventListener('click', handleImpact);

  // Клік по картці пресета — “роняємо” його
  document.getElementById('savedList').addEventListener('click', (e) => {
    const card = e.target.closest('.preset-card');
    if (!card) return;
    simulatePreset(card.dataset.id);
  });
}

// Рендер карток пресетів у вкладці "Збережені"
function renderSavedPresets() {
  const list = document.getElementById('savedList');
  list.innerHTML = PRESET_METEORS.map(p => `
    <div class="card preset-card cursor-pointer" data-id="${p.id}">
      <div class="card-title">${p.title}</div>
      <div class="card-description">${p.sub}</div>
      <div class="text-xs text-gray-600">
        ${p.params.size} м • ${p.params.speed} км/с • ${p.params.angle}° • ${matLabel(p.params.material)}
      </div>
      <div class="text-xs mt-1">${p.info}</div>
      <div class="mt-2">
        <button class="btn btn-sm btn-secondary">Роняти тут 💥</button>
      </div>
    </div>
  `).join('');
}

function matLabel(v) {
  if (v === 'iron') return 'залізний';
  if (v === 'ice') return 'льодяний';
  return 'кам’яний';
}

// Запуск симуляції для пресета на поточних координатах/сценарії
async function simulatePreset(presetId) {
  const p = PRESET_METEORS.find(x => x.id === presetId);
  if (!p) return;

  if (!window.APP_STATE?.selectedCoords) {
    alert('Спочатку обери точку на мапі.');
    return;
  }

  const params = {
    lat: window.APP_STATE.selectedCoords.lat,
    lon: window.APP_STATE.selectedCoords.lng,
    size: p.params.size,
    speed: p.params.speed,
    angle: p.params.angle,
    material: p.params.material,
    scenario: window.APP_STATE.currentScenario || 'ground'
  };

  try {
    const result = await callImpactAPI(params);
    window.APP_STATE.currentImpact = result;
    drawImpactEffects(result.layers);
    showResults(result);
  } catch (err) {
    alert('Помилка: ' + err.message);
  }
}

// Виклик “ручного” удару (без будь-яких збережень)
async function handleImpact() {
  if (!window.APP_STATE?.selectedCoords) return;

  const params = {
    lat: window.APP_STATE.selectedCoords.lat,
    lon: window.APP_STATE.selectedCoords.lng,
    size: parseFloat(document.getElementById('size').value),
    speed: parseFloat(document.getElementById('speed').value),
    angle: parseFloat(document.getElementById('angle').value),
    material: document.getElementById('material').value,
    scenario: window.APP_STATE.currentScenario || 'ground'
  };

  try {
    const result = await callImpactAPI(params);
    window.APP_STATE.currentImpact = result;
    drawImpactEffects(result.layers);
    showResults(result);
  } catch (err) {
    alert('Помилка: ' + err.message);
  }
}

// Експорт для використання в HTML
window.openArticle = openArticle;
