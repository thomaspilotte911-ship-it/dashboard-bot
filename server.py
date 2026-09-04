import os
import time
import datetime

from flask import Flask, request, jsonify

import state


def _iso(ts: float) -> str:
    return datetime.datetime.utcfromtimestamp(ts).isoformat() + "Z"


def _is_authorized() -> bool:
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    return bool(token) and token == os.environ.get("DASHBOARD_TOKEN")


def create_app() -> Flask:
    app = Flask(__name__, static_folder="public", static_url_path="")

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json(silent=True) or {}
        token = data.get("token")
        if token and token == os.environ.get("DASHBOARD_TOKEN"):
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": "Token invalide"}), 401

    @app.route("/api/stats")
    def get_stats():
        if not _is_authorized():
            return jsonify({"error": "Non autorisé"}), 401
        return jsonify(
            {
                "guildCount": state.stats["guild_count"],
                "userCount": state.stats["user_count"],
                "commandsUsed": state.stats["commands_used"],
                "status": state.stats["status"],
                "uptimeSeconds": int(time.time() - state.stats["started_at"]),
            }
        )

    @app.route("/api/logs")
    def get_logs():
        if not _is_authorized():
            return jsonify({"error": "Non autorisé"}), 401
        return jsonify(
            [
                {"timestamp": _iso(log["timestamp"]), "level": log["level"], "message": log["message"]}
                for log in state.logs
            ]
        )

    @app.route("/api/config", methods=["GET"])
    def get_config():
        if not _is_authorized():
            return jsonify({"error": "Non autorisé"}), 401
        return jsonify(state.get_config())

    @app.route("/api/config", methods=["POST"])
    def post_config():
        if not _is_authorized():
            return jsonify({"error": "Non autorisé"}), 401
        updates = request.get_json(silent=True) or {}
        return jsonify(state.save_config(updates))

    return app
