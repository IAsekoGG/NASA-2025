// Модуль статей
export function initArticles() {
    const modal = document.getElementById('articleModal');
    const closeBtn = document.getElementById('closeModal');
    
    // Закриття модального вікна
    closeBtn.addEventListener('click', closeArticle);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeArticle();
    });
    
    // ESC для закриття
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeArticle();
    });
}

export async function openArticle(articleId) {
    const modal = document.getElementById('articleModal');
    const content = document.getElementById('articleContent');
    
    try {
        const response = await fetch(`articles/${articleId}.html`);
        const html = await response.text();
        
        content.innerHTML = html;
        modal.classList.remove('hidden');
        
    } catch (err) {
        content.innerHTML = `
            <div class="article">
                <h1>❌ Стаття не знайдена</h1>
                <p>Вибачте, стаття "${articleId}" ще не створена.</p>
            </div>
        `;
        modal.classList.remove('hidden');
    }
}

function closeArticle() {
    const modal = document.getElementById('articleModal');
    modal.classList.add('hidden');
}