const BLOG_API_BASE_URL = 'http://127.0.0.1:5000';

const articleForm = document.getElementById('articleForm');
const articlesList = document.getElementById('dynamicArticles');

function renderArticle(article) {
    const articleElement = document.createElement('article');
    articleElement.className = 'box post dynamic-article';

    const header = document.createElement('header');
    const title = document.createElement('h2');
    const summary = document.createElement('p');
    const content = document.createElement('p');

    title.textContent = article.title;
    summary.textContent = article.summary;
    content.textContent = article.content;

    header.appendChild(title);
    header.appendChild(summary);
    articleElement.appendChild(header);
    articleElement.appendChild(content);

    return articleElement;
}

async function loadArticles() {
    if (!articlesList) return;

    try {
        const response = await fetch(`${BLOG_API_BASE_URL}/articles`);
        const data = await response.json();

        articlesList.innerHTML = '';

        if (!data.articles || data.articles.length === 0) {
            articlesList.innerHTML = '<p>Поки що додаткових статей немає.</p>';
            return;
        }

        data.articles.forEach((article) => {
            articlesList.appendChild(renderArticle(article));
        });
    } catch (error) {
        articlesList.innerHTML = '<p>Не вдалося завантажити додані статті.</p>';
        console.error(error);
    }
}

function setArticleStatus(text, isError = false) {
    const status = document.getElementById('articleStatus');

    if (!status) return;

    status.textContent = text;
    status.style.color = isError ? '#b00020' : '#2e7d32';
}

if (articleForm) {
    articleForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const payload = {
            title: articleForm.querySelector('[name="title"]').value.trim(),
            summary: articleForm.querySelector('[name="summary"]').value.trim(),
            content: articleForm.querySelector('[name="content"]').value.trim()
        };

        if (!payload.title || !payload.summary || !payload.content) {
            setArticleStatus('Заповніть назву, короткий опис і текст статті.', true);
            return;
        }

        try {
            const response = await fetch(`${BLOG_API_BASE_URL}/articles`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (!response.ok) {
                setArticleStatus(data.error || 'Не вдалося додати статтю.', true);
                return;
            }

            articleForm.reset();
            setArticleStatus('Статтю додано.');
            await loadArticles();
        } catch (error) {
            setArticleStatus('Не вдалося підключитися до сервера.', true);
            console.error(error);
        }
    });
}

loadArticles();
