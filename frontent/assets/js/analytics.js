const ANALYTICS_API_BASE_URL = 'http://127.0.0.1:5000';

const topicLabels = {
    faq: 'FAQ',
    contacts: 'Контакти',
    services: 'Послуги',
    about: 'Про нас',
    delivery: 'Доставка',
    payment: 'Оплата',
    returns: 'Повернення',
    navigation: 'Навігація',
    support: 'Підтримка',
    gpt: 'GPT-відповіді',
    unknown: 'Невідомі запити'
};

function getTopicEntries(data) {
    return Object.entries(topicLabels).map(([key, label]) => ({
        key,
        label,
        value: Number(data[key] || 0)
    }));
}

function renderAnalytics(data) {
    const totalElement = document.getElementById('analyticsTotal');
    const topElement = document.getElementById('analyticsTop');
    const barsElement = document.getElementById('analyticsBars');

    if (!totalElement || !topElement || !barsElement) return;

    const entries = getTopicEntries(data);
    const total = Number(data.total_messages || 0);
    const maxValue = Math.max(...entries.map((entry) => entry.value), 1);
    const topTopic = entries.reduce((best, entry) => (
        entry.value > best.value ? entry : best
    ), entries[0]);

    totalElement.textContent = total;
    topElement.textContent = topTopic.value > 0 ? topTopic.label : 'Немає даних';
    barsElement.innerHTML = '';

    entries.forEach((entry) => {
        const row = document.createElement('div');
        row.className = 'analytics-row';

        const label = document.createElement('span');
        label.className = 'analytics-topic';
        label.textContent = entry.label;

        const track = document.createElement('div');
        track.className = 'analytics-track';

        const bar = document.createElement('div');
        bar.className = 'analytics-fill';
        bar.style.width = `${Math.round((entry.value / maxValue) * 100)}%`;

        const value = document.createElement('strong');
        value.className = 'analytics-value';
        value.textContent = entry.value;

        track.appendChild(bar);
        row.appendChild(label);
        row.appendChild(track);
        row.appendChild(value);
        barsElement.appendChild(row);
    });
}

async function loadAnalytics() {
    const barsElement = document.getElementById('analyticsBars');

    if (!barsElement) return;

    try {
        const response = await fetch(`${ANALYTICS_API_BASE_URL}/analytics`);
        const data = await response.json();

        if (!response.ok) {
            barsElement.innerHTML = '<p>Не вдалося завантажити аналітику.</p>';
            return;
        }

        renderAnalytics(data);
    } catch (error) {
        barsElement.innerHTML = '<p>Не вдалося підключитися до сервера аналітики.</p>';
        console.error(error);
    }
}

loadAnalytics();
setInterval(loadAnalytics, 15000);
