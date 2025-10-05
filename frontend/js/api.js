// Модуль для роботи з API
// Для продакшену змінити на свій домен
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'
    : 'https://uptight-nita-znai-018677b1.koyeb.app/';

export async function callImpactAPI(params) {
    try {
        const response = await fetch(`${API_URL}/impact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            throw new Error('Помилка сервера');
        }
        
        return await response.json();
        
    } catch (err) {
        console.error('API Error:', err);
        throw new Error('Не вдалося підключитися до бекенду. Переконайся, що сервер запущений.');
    }
}