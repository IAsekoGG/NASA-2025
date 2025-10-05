export function initResultsPanel() {
  console.log('✅ Results panel готова');
}

export function showResults(data) {
  const panel = document.getElementById('resultsPanel');
  const isWaterScenario = data.scenario === 'water';
  
  let html = `
    <div class="panel-header">
      <div class="panel-title">
        Consequences of the impact <button class="btn-close" id="closeResultsPanel">&times;</button>
      </div>
    </div>
    <div class="panel-body">
      <div class="results-grid">
        <!-- ЕНЕРГІЯ -->
        <div class="result-card">
          <h3 class="card-title">Energy</h3>
          <div class="stat-grid">
            <div class="stat-card">
              <div class="stat-label">Impact energy</div>
              <div class="stat-value">${formatNumber(data.energy.energy_mt)} MT</div>
              <div class="stat-sub">≈ ${formatNumber(data.energy.hiroshima_eq)} bombs on Hiroshima</div>
            </div>
          </div>
        </div>

        <!-- КРАТЕР (умовно) -->
        ${data.crater ? `
        <div class="result-card">
          <h3 class="card-title">Crater</h3>
          <div class="stat-grid">
            <div class="stat-card">
              <div class="stat-label">Diameter</div>
              <div class="stat-value">${data.crater.diameter_km} km</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Depth</div>
              <div class="stat-value">${data.crater.depth_km} km</div>
            </div>
          </div>
        </div>
        ` : ''}
      </div>
    </div>

      <div class="results-stack">

        ${!isWaterScenario && data.casualties ? `
        <!-- 1) Людські втрати -->
        <div class="result-row casualties">
          <h3 class="row-title">Human losses</h3>
          <div class="location-info">
            ${data.location.nearest_city} (${data.location.area_type}),
            ${formatNumber(data.location.density)} people/km²
          </div>
          <div class="row-body">
            <div class="pill pill-dead"><b>Dead:</b> ${formatNumber(data.casualties.total_deaths)}</div>
            <div class="pill pill-hurt"><b>Hurt:</b> ${formatNumber(data.casualties.total_injuries)}</div>
            <div class="pill pill-affected"><b>Affected:</b> ${formatNumber(data.casualties.affected_population)}</div>
          </div>
        </div>
        ` : ''}

        ${!isWaterScenario && data.economic_damage ? `
        <!-- 2) Економічні збитки -->
        <div class="result-row economic">
          <h3 class="row-title">Economic losses</h3>
          <div class="row-body">
            <div class="pill pill-losses"><b>Total losses:</b> ${formatMoney(data.economic_damage.total_damage_usd)}</div>
            <div class="pill pill-area"><b>Affected area:</b> ${formatNumber(data.economic_damage.affected_area_km2)} km²</div>
          </div>
        </div>
        ` : ''}

        <!-- 3) Повне знищення (червоний) -->
        <div class="badge-rect rect-red">
          <div class="rect-title">Complete destruction</div>
          <div class="rect-sub">
            radius:
            ${
              (data.destruction && data.destruction.total_km) ??
              (data.airblast && data.airblast[0]?.radius_km) ?? '—'
            } km
          </div>
        </div>

        <!-- 4) Важкі руйнування (рожевий) -->
        <div class="badge-rect rect-pink">
          <div class="rect-title">Severe destruction</div>
          <div class="rect-sub">
            радіус:
            ${
              (data.destruction && data.destruction.heavy_km) ??
              (data.airblast && data.airblast[1]?.radius_km) ?? '—'
            } km
          </div>
        </div>

        <!-- 5) Середні руйнування (жовтий) -->
        <div class="badge-rect rect-yellow">
          <div class="rect-title">Average destruction</div>
          <div class="rect-sub">
            radius:
            ${
              (data.destruction && data.destruction.moderate_km) ??
              (data.airblast && data.airblast[2]?.radius_km) ?? '—'
            } km
          </div>
        </div>

        <!-- 6) Опіки 3 ступеня (жовтий + чорний бордер) -->
        <div class="badge-rect rect-burn rect-burn-yellow">
          <div class="rect-title">3rd degree burns</div>
          <div class="rect-sub">
            radius:
            ${
              (data.thermal && (data.thermal.third_deg_km ?? data.thermal[0]?.radius_km)) ?? '—'
            } км
          </div>
        </div>

        <!-- 7) Опіки 2 ступеня (жовтий + чорний бордер) -->
        <div class="badge-rect rect-burn rect-burn-yellow">
          <div class="rect-title">2nd degree burns</div>
          <div class="rect-sub">
            radius:
            ${
              (data.thermal && (data.thermal.second_deg_km ?? data.thermal[1]?.radius_km)) ?? '—'
            } км
          </div>
        </div>

        <!-- 8) Факт (блакитний) -->
        <div class="badge-rect rect-fact">
          <div class="rect-title"><img src="img/star_fall.svg" alt="свинка" class="svynka-icon">Fact</div>
          <div class="rect-sub">
            ${data.fun_fact || 'Наприклад: енергія зростає приблизно квадратично зі швидкістю (E ∝ v²).'}
          </div>
        </div>

      </div>
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
  if (usd >= 1e12) return '$' + (usd / 1e12).toFixed(1) + ' trillion';
  if (usd >= 1e9) return '$' + (usd / 1e9).toFixed(1) + ' billion';
  if (usd >= 1e6) return '$' + (usd / 1e6).toFixed(1) + ' million';
  return '$' + (usd / 1e3).toFixed(0) + 'K';
}

function translateZone(type) {
  const types = {
    'total_destruction': 'Total destruction',
    'heavy_damage': 'Heavy_damage',
    'moderate_damage': 'Moderate_damage',
    'light_damage': 'Light damage',
    'glass_breakage': 'Glass breakage'
  };
  return types[type] || type;
}

