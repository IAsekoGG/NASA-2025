export function initResultsPanel() {
  console.log('✅ Results panel готова');
}

export function showResults(data) {
  const panel = document.getElementById('resultsPanel');
  const isWaterScenario = data.scenario === 'water';
  
  let html = `
    <div class="panel-header">
      <div class="panel-title">📊 Наслідки удару</div>
      <button class="btn-close" onclick="document.getElementById('resultsPanel').classList.add('hidden')">✕</button>
    </div>
    
    <div class="panel-body">
      <div class="result-section">
        <h3>⚡ Енергія</h3>
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-label">Енергія удару</div>
            <div class="stat-value">${formatNumber(data.energy.energy_mt)} МТ</div>
            <div class="stat-sub">≈ ${formatNumber(data.energy.hiroshima_eq)} бомб на Хіросіму</div>
          </div>
        </div>
      </div>

      ${data.crater ? `
      <div class="result-section">
        <h3>🕳️ Кратер</h3>
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-label">Діаметр</div>
            <div class="stat-value">${data.crater.diameter_km} км</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Глибина</div>
            <div class="stat-value">${data.crater.depth_km} км</div>
          </div>
        </div>
      </div>
      ` : ''}

      ${data.airblast ? `
      <div class="result-section">
        <h3>💥 Ударна хвиля</h3>
        <div class="zones-list">
          ${data.airblast.slice(0, 3).map(zone => `
            <div class="zone-item">
              <div class="zone-color" style="background: ${zone.color}"></div>
              <div class="zone-info">
                <div class="zone-name">${translateZone(zone.type)}</div>
                <div class="zone-stats">${zone.radius_km} км • ${zone.pressure_kpa} кПа</div>
                <div class="zone-effects">${zone.effects}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
      ` : ''}

      ${data.thermal ? `
      <div class="result-section">
        <h3>🔥 Теплове випромінювання</h3>
        <div class="thermal-info">
          ${data.thermal.slice(0, 2).map(zone => `
            <div class="thermal-zone">
              <strong>${zone.effects}</strong> - ${zone.radius_km} км (${zone.temperature_c}°C)
            </div>
          `).join('')}
        </div>
      </div>
      ` : ''}

      ${!isWaterScenario && data.casualties ? `
      <div class="result-section alert-danger">
        <h3>💀 Людські втрати</h3>
        <div class="location-info">
          📍 ${data.location.nearest_city} (${data.location.area_type}), 
          👥 ${formatNumber(data.location.density)} люд/км²
        </div>
        <div class="stat-grid">
          <div class="stat-card danger">
            <div class="stat-label">Загиблі</div>
            <div class="stat-value">${formatNumber(data.casualties.total_deaths)}</div>
          </div>
          <div class="stat-card warning">
            <div class="stat-label">Поранені</div>
            <div class="stat-value">${formatNumber(data.casualties.total_injuries)}</div>
          </div>
          <div class="stat-card info">
            <div class="stat-label">Постраждало</div>
            <div class="stat-value">${formatNumber(data.casualties.affected_population)}</div>
          </div>
        </div>
      </div>
      ` : ''}

      ${!isWaterScenario && data.economic_damage ? `
      <div class="result-section alert-warning">
        <h3>💰 Економічні збитки</h3>
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-label">Загальні збитки</div>
            <div class="stat-value">${formatMoney(data.economic_damage.total_damage_usd)}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Уражена площа</div>
            <div class="stat-value">${formatNumber(data.economic_damage.affected_area_km2)} км²</div>
          </div>
        </div>
      </div>
      ` : ''}

      ${data.tsunami ? `
      <div class="result-section">
        <h3>🌊 Цунамі</h3>
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-label">Початкова висота</div>
            <div class="stat-value">${data.tsunami.initial_height_m} м</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Швидкість хвилі</div>
            <div class="stat-value">${data.tsunami.wave_speed_kmh} км/год</div>
          </div>
        </div>
        <div class="tsunami-zones">
          ${data.tsunami.zones.slice(0, 3).map(z => `
            <div class="tsunami-zone">
              <strong>${z.distance_km} км:</strong> висота ${z.wave_height_m} м, 
              прибуття через ${z.arrival_time_min} хв
            </div>
          `).join('')}
        </div>
      </div>
      ` : ''}

      ${data.strategic_risks && data.strategic_risks.length > 0 ? `
      <div class="result-section alert-critical">
        <h3>⚠️ Стратегічні ризики</h3>
        ${data.strategic_risks.map(risk => `
          <div class="risk-item ${risk.severity}">
            <div class="risk-icon">${getRiskIcon(risk.type)}</div>
            <div class="risk-text">${risk.description}</div>
          </div>
        `).join('')}
      </div>
      ` : ''}

      <div class="fun-fact">💡 ${data.fun_fact}</div>
    </div>
  `;

  panel.innerHTML = html;
  panel.classList.remove('hidden');
}

function formatNumber(num) {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M';
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'K';
  return num.toFixed(0);
}

function formatMoney(usd) {
  if (usd >= 1e12) return '$' + (usd / 1e12).toFixed(1) + ' трлн';
  if (usd >= 1e9) return '$' + (usd / 1e9).toFixed(1) + ' млрд';
  if (usd >= 1e6) return '$' + (usd / 1e6).toFixed(1) + ' млн';
  return '$' + (usd / 1e3).toFixed(0) + 'K';
}

function translateZone(type) {
  const types = {
    'total_destruction': 'Повне знищення',
    'heavy_damage': 'Важкі руйнування',
    'moderate_damage': 'Середні руйнування',
    'light_damage': 'Легкі руйнування',
    'glass_breakage': 'Вибиті вікна'
  };
  return types[type] || type;
}

function getRiskIcon(type) {
  const icons = {
    'nuclear': '☢️',
    'major_city': '🏙️',
    'industrial': '🏭'
  };
  return icons[type] || '⚠️';
}