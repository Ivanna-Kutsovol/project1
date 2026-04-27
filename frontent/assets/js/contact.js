const CONTACT_API_BASE_URL = 'http://127.0.0.1:5000';

function getContactFields(form) {
    return {
        name: form.querySelector('[name="name"]'),
        email: form.querySelector('[name="email"]'),
        message: form.querySelector('[name="message"]')
    };
}

function setFormStatus(form, text, isError = false) {
    let status = form.querySelector('.form-status');

    if (!status) {
        status = document.createElement('p');
        status.className = 'form-status';
        form.appendChild(status);
    }

    status.textContent = text;
    status.style.color = isError ? '#b00020' : '#2e7d32';
    status.style.marginTop = '1em';
}

document.querySelectorAll('form').forEach((form) => {
    const fields = getContactFields(form);

    if (!fields.name || !fields.email || !fields.message) {
        return;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const payload = {
            name: fields.name.value.trim(),
            email: fields.email.value.trim(),
            message: fields.message.value.trim()
        };

        if (!payload.name || !payload.email || !payload.message) {
            setFormStatus(form, 'Заповніть ім’я, email та повідомлення.', true);
            return;
        }

        try {
            const response = await fetch(`${CONTACT_API_BASE_URL}/contact`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (!response.ok) {
                setFormStatus(form, data.error || 'Не вдалося надіслати повідомлення.', true);
                return;
            }

            form.reset();
            setFormStatus(form, 'Повідомлення збережено. Дякуємо за звернення!');
        } catch (error) {
            setFormStatus(form, 'Не вдалося підключитися до сервера.', true);
            console.error(error);
        }
    });
});
