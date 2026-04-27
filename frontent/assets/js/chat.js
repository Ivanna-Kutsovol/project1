const API_BASE_URL = 'http://127.0.0.1:5000';

function ensureChatWidget() {
    if (document.getElementById('chat') && document.getElementById('openChat')) {
        return;
    }

    const widget = document.createElement('div');
    widget.innerHTML = `
        <div id="openChat" class="circle">
            <img class="icon" src="images/assistant.svg" alt="chatBot">
        </div>
        <div id="chat" class="chatBot">
            <div class="headerChat">
                <span class="titleChat">ChatBot</span>
                <button id="closeChat" type="button" class="close">X</button>
            </div>
            <div id="chatBody" class="bodyChat">
                <div class="chatMessageRow botMessageRow">
                    <div class="avatar">
                        <img class="iconChat" src="images/assistant.svg" alt="chatBot">
                    </div>
                    <div class="message">
                        <p>Привіт! Я - чат-бот. Напишіть своє запитання або скористайтеся швидкими кнопками.</p>
                        <div class="speedBtn" id="speedBtn">
                            <button type="button" id="faq" class="faq">FAQ</button>
                            <button type="button" id="contact" class="contact">Контакти</button>
                            <button type="button" id="about" class="about">Про нас</button>
                            <button type="button" id="delivery" class="delivery">Доставка</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="footerChat">
                <input id="inputChat" class="inputChat" type="text" placeholder="Написати повідомлення">
                <div id="sendBtn" class="send">
                    <img class="sendIcon" src="images/send.svg" alt="send">
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(widget);
}

ensureChatWidget();

const input = document.getElementById('inputChat');
const sendBtn = document.getElementById('sendBtn');
const chatBody = document.getElementById('chatBody');
const closeChat = document.getElementById('closeChat');
const openChat = document.getElementById('openChat');
const chat = document.getElementById('chat');
const titleChat = document.querySelector('.titleChat');

const faqBtn = document.getElementById('faq');
const contactsBtn = document.getElementById('contact');
const aboutBtn = document.getElementById('about');
const deliveryBtn = document.getElementById('delivery');

let messages = [];

let sessionId = localStorage.getItem('sessionId');
if (!sessionId) {
    sessionId = Date.now().toString();
    localStorage.setItem('sessionId', sessionId);
}

function setChatOpen(isOpen) {
    if (!openChat || !chat) return;

    if (isOpen) {
        chat.style.display = 'block';
        openChat.style.display = 'none';
        localStorage.setItem('chatOpen', 'true');
        input?.focus();
        return;
    }

    chat.style.display = 'none';
    openChat.style.display = 'block';
    localStorage.setItem('chatOpen', 'false');
}

if (localStorage.getItem('chatOpen') === 'true') {
    setChatOpen(true);
}

if (titleChat) {
    titleChat.addEventListener('click', (event) => {
        event.preventDefault();
        input?.focus();
    });
}

if (openChat && closeChat && chat) {
    openChat.addEventListener('click', () => setChatOpen(true));
    closeChat.addEventListener('click', () => setChatOpen(false));
}

function addMessage(text, isUser = true, save = true) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('message-wrapper');

    const message = document.createElement('div');
    message.classList.add('message');
    message.textContent = text;

    if (isUser) {
        wrapper.style.justifyContent = 'flex-end';
        message.style.background = '#3f51b5';
        message.style.color = '#fff';
    } else {
        wrapper.style.justifyContent = 'flex-start';

        const avatar = document.createElement('div');
        avatar.classList.add('avatar');

        const img = document.createElement('img');
        img.src = 'images/assistant.svg';
        img.classList.add('iconChat');

        avatar.appendChild(img);
        wrapper.appendChild(avatar);

        message.style.background = '#fff';
        message.style.color = '#202127';
    }

    wrapper.appendChild(message);
    chatBody.appendChild(wrapper);
    chatBody.scrollTop = chatBody.scrollHeight;

    if (save) {
        messages.push({
            text: text,
            isUser: isUser
        });
        localStorage.setItem('messages', JSON.stringify(messages));
    }
}

const storedMessages = localStorage.getItem('messages');
if (storedMessages) {
    messages = JSON.parse(storedMessages);
    messages.forEach((msg) => {
        addMessage(msg.text, msg.isUser, false);
    });
}

async function sendTextToBot(text) {
    const cleanText = text.trim();

    if (cleanText === '') return;

    setChatOpen(true);
    addMessage(cleanText, true);

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: cleanText,
                sessionId: sessionId
            })
        });

        const data = await response.json();

        if (!response.ok) {
            addMessage('Сталася помилка: ' + (data.error || 'невідома помилка'), false);
            setChatOpen(true);
            return;
        }

        addMessage(data.reply, false);
    } catch (error) {
        addMessage('Не вдалося підключитися до сервера.', false);
        console.error(error);
    } finally {
        setChatOpen(true);
        input?.focus();
    }
}

async function sendMessage() {
    const text = input.value.trim();

    if (text === '') return;

    input.value = '';
    await sendTextToBot(text);
}

if (sendBtn) {
    sendBtn.addEventListener('click', async (event) => {
        event.preventDefault();
        await sendMessage();
    });
}

if (input) {
    input.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            await sendMessage();
        }
    });
}

if (faqBtn) {
    faqBtn.addEventListener('click', async () => {
        await sendTextToBot('FAQ');
    });
}

if (contactsBtn) {
    contactsBtn.addEventListener('click', async () => {
        await sendTextToBot('контакти');
    });
}

if (aboutBtn) {
    aboutBtn.addEventListener('click', async () => {
        await sendTextToBot('про нас');
    });
}

if (deliveryBtn) {
    deliveryBtn.addEventListener('click', async () => {
        await sendTextToBot('доставка');
    });
}
