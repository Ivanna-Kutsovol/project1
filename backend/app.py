from flask import Flask, jsonify, request
from flask_cors import CORS

from analytics import get_analytics, increment_topic, increment_total
from bot_logic import get_reply
from session_store import add_message, get_history
from storage import create_article, init_db, list_articles, save_contact

app = Flask(__name__)
CORS(app)
init_db()

@app.route("/chat", methods=["POST"])
def chat() -> tuple:
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    message = str(data.get("message", "")).strip()
    session_id = str(data.get("sessionId", "")).strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    if not session_id:
        return jsonify({"error": "sessionId is required"}), 400

    history = get_history(session_id)

    reply, topic = get_reply(message, history)

    add_message(session_id, "user", message)
    add_message(session_id, "assistant", reply)

    increment_total()
    increment_topic(topic)

    return jsonify({
        "reply": reply,
        "topic": topic,
        "sessionId": session_id
    }), 200


@app.route("/analytics", methods=["GET"])
def analytics() -> tuple:
    return jsonify(get_analytics()), 200


@app.route("/history/<session_id>", methods=["GET"])
def history(session_id: str) -> tuple:
    return jsonify({
        "sessionId": session_id,
        "history": get_history(session_id)
    }), 200


@app.route("/contact", methods=["POST"])
def contact() -> tuple:
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not email or not message:
        return jsonify({"error": "Name, email and message are required"}), 400

    contact_message = save_contact(name, email, message)
    return jsonify({
        "message": "Contact message saved",
        "contact": contact_message
    }), 201


@app.route("/articles", methods=["GET"])
def articles() -> tuple:
    return jsonify({"articles": list_articles()}), 200


@app.route("/articles", methods=["POST"])
def add_article() -> tuple:
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    title = str(data.get("title", "")).strip()
    summary = str(data.get("summary", "")).strip()
    content = str(data.get("content", "")).strip()

    if not title or not summary or not content:
        return jsonify({"error": "Title, summary and content are required"}), 400

    article = create_article(title, summary, content)
    return jsonify({
        "message": "Article created",
        "article": article
    }), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)
