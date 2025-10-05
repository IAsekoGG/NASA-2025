// Модуль для роботи з API
// Для продакшену змінити на свій домен
const RAW_API =
  window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://uptight-nita-znai-018677b1.koyeb.app';

const API_BASE = RAW_API.replace(/\/+$/, ''); // зрізаємо трейлінг-слеші

// 2) Універсальний fetch з таймаутом
async function fetchJSON(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, { ...options, signal: controller.signal });

    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(
        `Помилка сервера (${res.status} ${res.statusText})${text ? `: ${text.slice(0, 200)}` : ''}`
      );
    }

    // інколи бек може повернути порожнє тіло
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) return await res.json();
    const txt = await res.text();
    try { return JSON.parse(txt); } catch { return { raw: txt }; }

  } finally {
    clearTimeout(id);
  }
}

// 3) Власне виклик ендпоінта
export async function callImpactAPI(params) {
  try {
    const url = `${API_BASE}/impact`; // дасть '/api/impact' або 'https://.../impact'
    return await fetchJSON(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
  } catch (err) {
    console.error('API Error:', err);
    // дружнє повідомлення користувачу
    throw new Error(
      err?.name === 'AbortError'
        ? 'Сервер довго не відповідає. Спробуйте ще раз.'
        : 'Не вдалося підключитися до бекенду. Перевірте налаштування API або спробуйте пізніше.'
    );
  }
}