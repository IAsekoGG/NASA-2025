// Модуль панелі "Врони метеорит"
import { callImpactAPI } from './api.js';
import { drawImpactEffects } from './map.js';
import { showResults } from './results-panel.js';
import { openArticle } from './articles.js';

window.APP_STATE = window.APP_STATE || {};
if (!window.APP_STATE.currentScenario) {
  window.APP_STATE.currentScenario = 'ground';
}

// === Educational bins & helpers ===
const SIZE_BINS = [
  { max: 2,    label: 'weekly–2 weeks',      note: 'Burns up high; sometimes fireballs', tag: '1–2 m',       color: '#10B981' },
  { max: 15,   label: 'yearly–few years',    note: 'Bright fireballs',                    tag: '≈10 m',       color: '#3B82F6' },
  { max: 30,   label: 'once per decade',     note: 'Airburst possible',                   tag: '≈20 m',       color: '#8B5CF6' },
  { max: 60,   label: 'once per century+',   note: 'Stony — airburst',                    tag: '50–60 m',     color: '#F59E0B' },
  { max: 120,  label: 'century–millennium',  note: 'Iron already cratering',              tag: '100 m',       color: '#EF4444' },
  { max: 200,  label: '~millennium',         note: 'Regional consequences',               tag: '140–200 m',   color: '#DC2626' },
  { max: 1500, label: '~hundreds of kyr',    note: 'Regional/global damage',              tag: '1 km',        color: '#991B1B' },
  { max: 15000,label: '~100 Myr',            note: 'Mass extinctions',                    tag: '10 km',       color: '#7F1D1D' },
];

const SPEED_BINS = [
  { max: 11.2, label: 'physical minimum', note: 'Lower entry limit',     tag: '≈11 km/s', color: '#6B7280' },
  { max: 15,   label: 'typical',          note: 'Asteroid entries',      tag: '12–15',    color: '#10B981' },
  { max: 20,   label: 'most common',      note: '≈peak distribution',    tag: '15–20',    color: '#3B82F6' },
  { max: 25,   label: 'less typical',     note: 'Still asteroids',       tag: '20–25',    color: '#8B5CF6' },
  { max: 40,   label: 'rare',             note: 'High velocity',         tag: '25–40',    color: '#F59E0B' },
  { max: 72,   label: 'very rare',        note: 'Mostly comets',         tag: '>40',      color: '#EF4444' },
];

function angleInfo(angleDeg) {
  if (angleDeg < 10)  return { label: 'Very rare <10° (~1.5%)', note: 'Flat trajectory, elongated ejecta', tag: '<10°',   color: '#EF4444' };
  if (angleDeg < 30)  return { label: 'Rare <30° (~13%)',       note: 'Larger ground pressure trace',     tag: '10–30°', color: '#F59E0B' };
  if (angleDeg <= 60) return { label: 'Most typical (~45°)',    note: 'Most efficient cratering',         tag: '30–60°', color: '#10B981' };
  return                 { label: 'Steep entry',                note: 'Higher penetration depth',         tag: '60–90°', color: '#3B82F6' };
}

const MATERIAL_FACTS = {
  stone: { title: "Stony (~94%)", dens: "ρ≈3.2 g/cm³", note: "Often breaks up in air → airbursts",             color: '#92400E', bgColor: '#FEF3C7' },
  iron:  { title: "Iron (~5%)",   dens: "ρ≈7.8 g/cm³", note: "Strong, penetrating → craters from smaller sizes", color: '#1F2937', bgColor: '#E5E7EB' },
  ice:   { title: "Cometary nucleus", dens: "ρ≈0.5 g/cm³", note: "Porous, fragments high → rarely craters",     color: '#1E40AF', bgColor: '#DBEAFE' },
};

const pickBin = (bins, x) => bins.find(b => x <= b.max) || bins[bins.length - 1];

// 10 готових пресетів для вкладки "Збережені" (без челябінська, для симуляції)
const PRESET_METEORS = [
  // Реальні падіння / історичні
  { id: 'hoba', title: 'Hoba', sub: 'Намібія, залізний', params: { size: 1000, speed: 12, angle: 20, material: 'iron' }, info: 'Largest meteorite ever found (soft landing).' },
  { id: 'allende', title: 'Allende', sub: 'Мексика, кам’яний', params: { size: 200, speed: 17, angle: 35, material: 'stone' }, info: 'CV3 chondrite, rich in early solar condensates.' },
  { id: 'murchison', title: 'Murchison', sub: 'Австралія, кам’яний', params: { size: 150, speed: 16, angle: 40, material: 'stone' }, info: 'CM2 chondrite, organics and amino acids.' },
  { id: 'ensisheim', title: 'Ensisheim', sub: 'Франція, 1492', params: { size: 120, speed: 15, angle: 45, material: 'stone' }, info: 'Classical historical chondrite.' },
  { id: 'diablo', title: 'Meteor Crater body', sub: 'США, залізний', params: { size: 50, speed: 15, angle: 45, material: 'iron' }, info: 'Predecessor of Barringer crater (estimated parameters).' },
  { id: 'peekskill', title: 'Peekskill', sub: 'США, 1992', params: { size: 10, speed: 15, angle: 55, material: 'stone' }, info: 'Famous fall captured on video.' },

  // Глобальні катастрофи / симуляції
  { id: 'chicxulub', title: 'Chicxulub Impactor', sub: '66 млн років тому', params: { size: 10000, speed: 20, angle: 45, material: 'stone' }, info: '≈10 km asteroid that caused the mass extinction of dinosaurs.' },

  // Близькі прольоти — змодельовані як гіпотетичне падіння
  { id: 'apophis2029', title: '99942 Apophis', sub: '13 квітня 2029', params: { size: 340, speed: 7.4, angle: 45, material: 'stone' }, info: 'It will fly safely in reality; here is a hypothetical hit.' },
  { id: 'duende2013', title: '2012 DA14 (Duende)', sub: '15 лютого 2013', params: { size: 50, speed: 7.8, angle: 45, material: 'stone' }, info: 'Low flight; here — like a simulated strike.' },
  { id: '2019ok', title: '2019 OK', sub: '25 липня 2019', params: { size: 120, speed: 24.6, angle: 45, material: 'stone' }, info: '"Sudden" rapprochement; hypothetical blow.' },
  { id: '2020qg', title: '2020 QG', sub: '16 серпня 2020', params: { size: 5, speed: 12.3, angle: 60, material: 'stone' }, info: 'Very close flyby; simulation of a small fireball.' }
];

window.APP_STATE = window.APP_STATE || {};
if (!window.APP_STATE.currentScenario) {
  window.APP_STATE.currentScenario = 'ground';
}

export function initImpactPanel() {
  const panel = document.getElementById('impactPanel');

  panel.innerHTML = `
    <div class="panel-header">
      <div class="panel-title">
        Launch the piggy-meteor
        <button class="btn-info" onclick="openArticle('asteroid-basics')"><img src="img/star.svg" alt="свинка" class="svynka-icon"></button>
      </div>
    </div>

    <div class="panel-body">
      <!-- Вкладки -->
      <div class="tabs">
        <div class="tab active" data-tab="params">Parameters</div>
        <div class="tab" data-tab="scenarios">Scenarios</div>
        <div class="tab" data-tab="saved">Saved</div>
      </div>

      <!-- Вкладка: Параметри -->
      <div class="tab-content active" id="tab-params">
        <div id="selectedCoords" class="text-sm text-gray-500 mb-4">Click on the map</div>

        <div class="input-group">
          <label class="input-label">
            Size (m)
            <button class="btn-info" onclick="openArticle('impact-effects')">
              <img src="img/star.svg" alt="info" class="svynka-icon">
            </button>
          </label>
          <div class="range-row">
            <input type="range" id="size" min="1" max="1500" step="1" value="100" class="input-range">
            <span id="sizeValue" class="input-value">100 m</span>
          </div>
          <div class="visual-scale" id="sizeScale"></div>
          <div id="sizeChips" class="edu-chips"></div>
        </div>

        <div class="input-group">
          <label class="input-label">
            Speed (km/s)
            <button class="btn-info" onclick="openArticle('speed')">
              <img src="img/star.svg" alt="info" class="svynka-icon">
            </button>
          </label>
          <div class="range-row">
            <input type="range" id="speed" min="5" max="72" step="0.1" value="20" class="input-range">
            <span id="speedValue" class="input-value">20 km/s</span>
          </div>
          <div class="visual-scale" id="speedScale"></div>
          <div id="speedChips" class="edu-chips"></div>
        </div>

        <div class="input-group">
          <label class="input-label">
            Angle of incidence (°)
            <button class="btn-info" onclick="openArticle('impact-effects')">
              <img src="img/star.svg" alt="info" class="svynka-icon">
            </button>
          </label>
          <div class="range-row">
            <input type="range" id="angle" min="0" max="90" step="1" value="45" class="input-range">
            <span id="angleValue" class="input-value">45°</span>
          </div>
          <div class="visual-scale" id="angleScale"></div>
          <div id="angleChips" class="edu-chips"></div>
        </div>

        <div class="input-group">
          <label class="input-label">
            Material
            <button class="btn-info" onclick="openArticle('impact-effects')">
              <img src="img/star.svg" alt="info" class="svynka-icon">
            </button>
          </label>
          <select id="material" class="w-full p-2 border rounded">
            <option value="stone">Stone</option>
            <option value="iron">Iron</option>
            <option value="ice">Ice</option>
          </select>
          <div id="materialCard" class="material-card"></div>
        </div>

        <button id="impactBtn" class="btn btn-primary w-full" disabled>
          LAUNCH THE PIGGY-METEOR <img src="img/pig.svg" alt="свинка" class="svynka-icon">
        </button>
      </div>

      <!-- Вкладка: Збережені -->
      <div class="tab-content" id="tab-saved">
        <div id="savedList" class="grid gap-2"></div>
      </div>

      <!-- Вкладка: Сценарії -->
      <div class="tab-content" id="tab-scenarios">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div class="card" data-scenario="water" onclick="selectScenario('water')">
                    <div class="card-title">
                        Into the water
                        <button class="btn-info" onclick="event.stopPropagation(); openArticle('water-impact')"><img src="img/star.svg" alt="свинка" class="svynka-icon"></button>
                    </div>
                </div>
                
                <div class="card selected" data-scenario="ground" onclick="selectScenario('ground')">
                    <div class="card-title">
                        On the ground
                        <button class="btn-info" onclick="event.stopPropagation(); openArticle('ground-impact')"><img src="img/star.svg" alt="свинка" class="svynka-icon"></button>
                    </div>
                </div>
                
                <div class="card" data-scenario="airburst" onclick="selectScenario('airburst')">
                    <div class="card-title">
                        In the atmosphere
                        <button class="btn-info" onclick="event.stopPropagation(); openArticle('airburst')"><img src="img/star.svg" alt="свинка" class="svynka-icon"></button>
                    </div>
                </div>
                
                <div class="card" data-scenario="fragmentation" onclick="selectScenario('fragmentation')">
                    <div class="card-title">
                      Split
                      <button class="btn-info" onclick="event.stopPropagation(); openArticle('split')"><img src="img/star.svg" alt="свинка" class="svynka-icon"></button>
                    </div>
                </div>
            </div>
            
            <!-- Додаткові параметри сценарію -->
            <div id="scenarioParams" class="mt-4"></div>
        </div>
      </div>
  `;

  setupEventListeners();
  document.querySelectorAll('.input-range').forEach(range => {
      const updateRange = e => {
        const min = e.target.min || 0;
        const max = e.target.max || 100;
        const val = e.target.value;
        const percent = ((val - min) / (max - min)) * 100;
        e.target.style.setProperty('--value', `${percent}%`);
      };
      range.addEventListener('input', updateRange);
      updateRange({ target: range }); // початкове оновлення
  });
  renderSavedPresets();
  updateEduHints();
  updateVisualScale('size', parseFloat(sizeEl.value));   // коли рухаєш size
  updateVisualScale('speed', parseFloat(speedEl.value)); // коли рухаєш speed
  updateVisualScale('angle', parseFloat(angleEl.value)); // коли рухаєш angle

  renderScenarioParams(window.APP_STATE.currentScenario || 'ground');
}

function renderScenarioParams(scenario) {
  const box = document.getElementById('scenarioParams');
  if (!box) return;

  const T = (html) => `<div class="scenario-params-card">${html}</div>`;

  if (scenario === 'water') {
    box.innerHTML = T(`
      <div class="param-row">
        <label>
Depth at impact point (m)</label>
        <input type="number" id="sp-water-depth" class="input" min="0" step="10" value="500">
      </div>
    `);
  } else if (scenario === 'airburst') {
    box.innerHTML = T(`
      <div class="param-row">
        <label>Explosion height (km)</label>
        <input type="number" id="sp-airburst-alt" class="input" min="1" max="50" step="1" value="15">
      </div>
    `);
  } else if (scenario === 'fragmentation') {
    box.innerHTML = T(`
      <div class="param-row">
        <label>Number of fragments</label>
        <input type="number" id="sp-frag-count" class="input" min="2" max="20" step="1" value="5">
      </div>
    `);
  } else { // ground (за замовчуванням)
    box.innerHTML = T(`
      <div class="param-row">
        <label>Soil type</label>
        <select id="sp-ground-soil" class="input">
          <option value="rock">rock</option>
          <option value="dry">dry</option>
          <option value="wet">wet</option>
          <option value="ice">ice</option>
        </select>
      </div>
    `);
  }
}

function selectScenario(name) {
  window.APP_STATE.currentScenario = name;
  const scope = document.getElementById('tab-scenarios');
  if (scope) {
    scope.querySelectorAll('.card[data-scenario]').forEach(c => {
      c.classList.toggle('selected', c.dataset.scenario === name);
    });
  }
  renderScenarioParams(name);
}
window.selectScenario = selectScenario;

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
    document.getElementById('sizeValue').textContent = e.target.value + ' m';
  };
  document.getElementById('speed').oninput = e => {
    document.getElementById('speedValue').textContent = e.target.value + ' km/s';
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

function renderVisualScales() {
  // SIZE scale
  const sizeScale = document.getElementById('sizeScale');
  if (sizeScale) {
    sizeScale.innerHTML = SIZE_BINS.map((bin, i) => {
      const prevMax = i > 0 ? SIZE_BINS[i-1].max : 0;
      const width = ((bin.max - prevMax) / 15000 * 100);
      return `<div class="scale-segment" style="width:${width}%; background:${bin.color}20; border-left:2px solid ${bin.color};">
                <span class="scale-label" style="color:${bin.color};">${bin.icon}</span>
              </div>`;
    }).join('');
  }

  // SPEED scale
  const speedScale = document.getElementById('speedScale');
  if (speedScale) {
    speedScale.innerHTML = SPEED_BINS.map((bin, i) => {
      const prevMax = i > 0 ? SPEED_BINS[i-1].max : 5;
      const width = ((bin.max - prevMax) / (72 - 5) * 100);
      return `<div class="scale-segment" style="width:${width}%; background:${bin.color}20; border-left:2px solid ${bin.color};">
                <span class="scale-label" style="color:${bin.color};">${bin.icon}</span>
              </div>`;
    }).join('');
  }

  // ANGLE scale (fixed 4 zones)
  const angleScale = document.getElementById('angleScale');
  if (angleScale) {
    const zones = [
      { max: 10, color: '#EF4444', icon: '↗', width: 11.1 },
      { max: 30, color: '#F59E0B', icon: '↗', width: 22.2 },
      { max: 60, color: '#10B981', icon: '↘', width: 33.3 },
      { max: 90, color: '#3B82F6', icon: '↓', width: 33.3 },
    ];
    angleScale.innerHTML = zones.map(z =>
      `<div class="scale-segment" style="width:${z.width}%; background:${z.color}20; border-left:2px solid ${z.color};">
         <span class="scale-label" style="color:${z.color};">${z.icon}</span>
       </div>`
    ).join('');
  }
}

function updateVisualScale(type, value) {
  const scaleEl = document.getElementById(`${type}Scale`);
  if (!scaleEl) return;

  const existing = scaleEl.querySelector('.scale-marker');
  if (existing) existing.remove();

  let pos = 0;
  if (type === 'size')   pos = (value / 10000) * 100;
  if (type === 'speed')  pos = ((value - 5) / (72 - 5)) * 100;
  if (type === 'angle')  pos = (value / 90) * 100;

  const marker = document.createElement('div');
  marker.className = 'scale-marker';
  marker.style.left = `${pos}%`;
  scaleEl.appendChild(marker);
}

function updateEduHints() {
  const size = parseFloat(document.getElementById('size').value);
  const speed = parseFloat(document.getElementById('speed').value);
  const angle = parseFloat(document.getElementById('angle').value);
  const material = document.getElementById('material').value;

  // SIZE chips/micro
  const sb = pickBin(SIZE_BINS, size);
  const sizeChips = document.getElementById('sizeChips');
  if (sizeChips) sizeChips.innerHTML = chipRow([
    { tag: sb.tag, label: sb.label, color: sb.color, icon: sb.icon },
  ]);

  // SPEED
  const sp = pickBin(SPEED_BINS, speed);
  const speedChips = document.getElementById('speedChips');
  if (speedChips) speedChips.innerHTML = chipRow([
    { tag: sp.tag, label: sp.label, color: sp.color, icon: sp.icon },
  ]);

  // ANGLE
  const ai = angleInfo(angle);
  const angleChips = document.getElementById('angleChips');
  if (angleChips) angleChips.innerHTML = chipRow([
    { tag: ai.tag, label: ai.label, color: ai.color, icon: ai.icon },
  ]);

  // MATERIAL pill
  const mf = MATERIAL_FACTS[material];
  const matCard = document.getElementById('materialCard');
  if (matCard && mf) {
    matCard.innerHTML = `
      <div class="material-pill" style="background:${mf.bgColor}; border-color:${mf.color};">
        <div class="material-header">
          <div>
            <div class="pill-title" style="color:${mf.color};">${mf.title}</div>
            <div class="pill-sub"   style="color:${mf.color}99;">${mf.dens}</div>
          </div>
        </div>
        <div class="pill-note"  style="color:${mf.color}DD;">${mf.note}</div>
      </div>
    `;
  }

  // кнопка активна лише при вибраній точці
  const hasCoords = !!window.APP_STATE?.selectedCoords;
  const btn = document.getElementById('impactBtn');
  if (btn) btn.disabled = !hasCoords;

  if (hasCoords && window.APP_STATE.selectedCoords) {
    const sel = document.getElementById('selectedCoords');
    if (sel) {
      sel.innerHTML = `
        <span class="coords-icon">✅</span>
        <span class="coords-text">
          <strong>Impact point:</strong> ${window.APP_STATE.selectedCoords.lat.toFixed(4)}°, ${window.APP_STATE.selectedCoords.lng.toFixed(4)}°
        </span>
      `;
    }
  }
}

function chipRow(items) {
  return `<div class="chips-row">
    ${items.map(i => `
      <span class="chip" style="background:${i.color}15; border-color:${i.color}; color:${i.color};">
        <b>${i.tag}</b>
        <span class="chip-label">${i.label}</span>
      </span>
    `).join('')}
  </div>`;
}

// Рендер карток пресетів у вкладці "Збережені"
function renderSavedPresets() {
  const list = document.getElementById('savedList');
  list.innerHTML = PRESET_METEORS.map(p => `
    <div class="card preset-card cursor-pointer" data-id="${p.id}">
      <div class="card-title">${p.title}</div>
      <div class="card-description">${p.sub}</div>
      <div class="text-xs text-gray-600">
        ${p.params.size} m • ${p.params.speed} km/s • ${p.params.angle}° • ${matLabel(p.params.material)}
      </div>
      <div class="text-xs mt-1">${p.info}</div>
      <div class="mt-2">
        <button class="btn btn-sm btn-secondary"> Launch here <img src="img/pig.svg" alt="свинка" class="svynka-icon"></button>
      </div>
    </div>
  `).join('');
}

renderScenarioParams(window.APP_STATE.currentScenario || 'ground');

function matLabel(v) {
  if (v === 'iron') return 'iron';
  if (v === 'ice') return 'ice';
  return 'stone';
}

// Запуск симуляції для пресета на поточних координатах/сценарії
async function simulatePreset(presetId) {
  const p = PRESET_METEORS.find(x => x.id === presetId);
  if (!p) return;

  if (!window.APP_STATE?.selectedCoords) {
    alert('First, select a point on the map.');
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
  if (params.scenario === 'water') {
    const depthInput = document.getElementById('sp-water-depth');
    params.water_depth = depthInput ? parseFloat(depthInput.value) : 4000;
  }
  try {
    const result = await callImpactAPI(params);
    window.APP_STATE.currentImpact = result;
    drawImpactEffects(result.layers);
    showResults(result);
  } catch (err) {
    alert('Error: ' + err.message);
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
  if (params.scenario === 'water') {
    const depthInput = document.getElementById('sp-water-depth');
    params.water_depth = depthInput ? parseFloat(depthInput.value) : 4000;
  }
  try {
    const result = await callImpactAPI(params);
    window.APP_STATE.currentImpact = result;
    drawImpactEffects(result.layers);
    showResults(result);
  } catch (err) {
    alert('Error: ' + err.message);
  }
}

// Експорт для використання в HTML
window.openArticle = openArticle;
