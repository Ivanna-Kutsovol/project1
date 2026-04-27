import os
from typing import Dict, List, Tuple

from openai import OpenAI


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

FALLBACK_REPLY = (
    "Я не зовсім зрозумів запитання. Спробуйте написати: FAQ, контакти, послуги, "
    "про нас, доставка, оплата, повернення або допомога з сайтом."
)
NO_API_KEY_REPLY = (
    "GPT зараз не підключений: сервер запущено без OPENAI_API_KEY. "
    "Задайте ключ у PowerShell і перезапустіть backend."
)
GPT_ERROR_REPLY = (
    "GPT зараз недоступний: не вдалося отримати відповідь від OpenAI API. "
    "Перевірте ключ, інтернет і перезапустіть backend."
)
GPT_QUOTA_REPLY = (
    "GPT зараз недоступний, бо на акаунті OpenAI перевищено квоту або не налаштовано оплату. "
    "Перевірте Billing/Usage у кабінеті OpenAI, поповніть баланс або додайте спосіб оплати."
)

SITE_CONTEXT = """
Ти чат-бот сайту Smart Support Hub.
Сайт демонструє веб-ресурс з інтегрованим чат-ботом для підтримки користувачів.
Основні сторінки: головна, FAQ, блог/новини, контакти.
Основні можливості: відповіді на часті запитання, допомога з навігацією, технічна підтримка,
інформація про послуги, оплату, доставку, повернення та контактні канали.

Контакти:
- Телефон: +38 (050) 000-00-00
- Email: support@example.com
- Країна: Україна

Правила відповіді:
- Відповідай мовою користувача.
- Відповідай коротко і зрозуміло, 2-5 речень.
- Якщо користувач питає, куди перейти на сайті, називай сторінку: головна, FAQ, блог або контакти.
- Якщо точної інформації немає, чесно скажи, що це демонстраційний проєкт, і запропонуй звернутися через контакти.
""".strip()


def detect_topic(message: str, history: List[Dict[str, str]]) -> str:
    text = message.strip().lower()

    wants_navigation = any(
        word in text
        for word in (
            "как перейти",
            "куди перейти",
            "куда перейти",
            "як перейти",
            "де знайти",
            "где найти",
            "відкрити",
            "открыть",
            "перейти",
            "навігац",
            "навигац",
        )
    )

    if wants_navigation:
        if any(word in text for word in ("послуг", "услуг", "сервіс", "сервис")):
            return "navigation_services"

        if "faq" in text:
            return "navigation_faq"

        if any(word in text for word in ("блог", "новин", "новост", "стат")):
            return "navigation_blog"

        if any(word in text for word in ("контак", "зв'яз", "звяз", "связ")):
            return "navigation_contacts"

        for item in reversed(history):
            if item["role"] != "user":
                continue

            old_text = item["text"].lower()

            if any(word in old_text for word in ("послуг", "услуг", "сервіс", "сервис")):
                return "navigation_services"

            if "faq" in old_text:
                return "navigation_faq"

            if any(word in old_text for word in ("блог", "новин", "новост", "стат")):
                return "navigation_blog"

            if any(word in old_text for word in ("контак", "зв'яз", "звяз", "связ")):
                return "navigation_contacts"

        return "navigation"

    if "faq" in text or "част" in text or "поширен" in text:
        return "faq"

    if any(word in text for word in ("контак", "зв'яз", "звяз", "связ", "email", "пошта", "почта")):
        return "contacts"

    if any(word in text for word in ("послуг", "услуг", "сервіс", "сервис")):
        return "services"

    if any(word in text for word in ("про нас", "про компан", "о нас", "smart support hub")):
        return "about"

    if any(word in text for word in ("достав", "delivery")):
        return "delivery"

    if any(word in text for word in ("оплат", "payment", "платеж")):
        return "payment"

    if any(word in text for word in ("повернен", "возврат", "return", "refund")):
        return "returns"

    if any(word in text for word in ("техніч", "техничес", "помилка", "ошибка", "не працю", "не работает")):
        return "support"

    if (
        "кількість днів" in text
        or "скільки днів" in text
        or "сколько дней" in text
        or "скільки займає" in text
        or "сколько занимает" in text
        or "як довго" in text
        or "как долго" in text
    ):
        for item in reversed(history):
            if item["role"] != "user":
                continue

            old_text = item["text"].lower()

            if "достав" in old_text:
                return "delivery_duration"

            if "контак" in old_text or "зв'яз" in old_text or "связ" in old_text:
                return "contacts_followup"

        return "unknown"

    if "телефон" in text or "номер" in text:
        return "contacts_phone"

    return "unknown"


def get_local_reply(topic: str) -> Tuple[str, str] | None:
    if topic == "faq":
        return "FAQ знаходиться у верхньому меню сайту. Натисніть пункт 'FAQ', щоб перейти до сторінки з поширеними запитаннями.", "faq"

    if topic == "contacts":
        return "Ось наші контакти: телефон +38(050) 000-00-00, email: support@example.com.", "contacts"

    if topic == "services":
        return (
            "Розділ послуг описує інформаційну підтримку, FAQ, навігацію по сайту, "
            "збереження контексту діалогу та аналітику звернень."
        ), "services"

    if topic == "about":
        return (
            "Smart Support Hub - це навчальний веб-ресурс з інтегрованим чат-ботом "
            "для підтримки користувачів."
        ), "about"

    if topic == "delivery":
        return "Інформація про доставку: стандартна доставка займає до 5 днів.", "delivery"

    if topic == "delivery_duration":
        return "Доставка займає до 5 днів.", "delivery"

    if topic == "contacts_phone":
        return "Ось наш телефон: +38(050) 000-00-00.", "contacts"

    if topic == "contacts_email":
        return "Ось наша пошта: support@example.com.", "contacts"

    if topic == "contacts_followup":
        return "Уточніть, будь ласка, що саме вас цікавить: телефон чи email?", "contacts"

    if topic == "payment":
        return "Оплату можна описати як демонстраційний сценарій: банківська картка або онлайн-оплата.", "payment"

    if topic == "returns":
        return "Для повернення товару або послуги зверніться через контакти та опишіть причину звернення.", "returns"

    if topic == "navigation":
        return "Основні розділи доступні у верхньому меню: Головна, FAQ, Блог і Контакти. Напишіть, яку саме сторінку хочете відкрити.", "navigation"

    if topic == "navigation_services":
        return "Щоб перейти до послуг, відкрийте головну сторінку і натисніть пункт 'Послуги' у верхньому меню. Також можна перейти до блоку можливостей на головній сторінці.", "navigation"

    if topic == "navigation_faq":
        return "Щоб перейти до FAQ, натисніть пункт 'FAQ' у верхньому меню сайту.", "navigation"

    if topic == "navigation_blog":
        return "Щоб перейти до блогу, натисніть пункт 'Блог' у верхньому меню сайту.", "navigation"

    if topic == "navigation_contacts":
        return "Щоб перейти до контактів, натисніть пункт 'Контакти' у верхньому меню або прокрутіть сторінку до форми зворотного зв’язку.", "navigation"

    if topic == "support":
        return "Опишіть проблему детальніше: що саме не працює, на якій сторінці і яку дію ви виконували.", "support"

    return None


def build_gpt_input(message: str, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    gpt_messages: List[Dict[str, str]] = [
        {"role": "system", "content": SITE_CONTEXT},
    ]

    for item in history[-8:]:
        role = "assistant" if item["role"] == "assistant" else "user"
        gpt_messages.append({"role": role, "content": item["text"]})

    gpt_messages.append({"role": "user", "content": message})
    return gpt_messages


def get_gpt_reply(message: str, history: List[Dict[str, str]]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return NO_API_KEY_REPLY

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=build_gpt_input(message, history),
            max_output_tokens=220,
        )
        return response.output_text.strip() or FALLBACK_REPLY
    except Exception as error:
        error_text = str(error).lower()
        print(f"OpenAI API error: {error}")

        if "insufficient_quota" in error_text or "exceeded your current quota" in error_text:
            return GPT_QUOTA_REPLY

        return GPT_ERROR_REPLY


def get_reply(message: str, history: List[Dict[str, str]]) -> Tuple[str, str]:
    topic = detect_topic(message, history)
    local_reply = get_local_reply(topic)

    if local_reply:
        return local_reply

    return get_gpt_reply(message, history), "gpt"
