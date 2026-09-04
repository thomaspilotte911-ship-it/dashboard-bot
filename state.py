import json
import time
import threading
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
MAX_LOGS = 200

_lock = threading.Lock()

DEFAULT_CONFIG = {
    "prefix": "!",
    "welcomeChannelId": "",
    "welcomeMessage": "Bienvenue {user} sur le serveur ! 🎉",
    "embedColor": "#5865F2",
    "botStatus": "En ligne | /help",
    "logCommandUsage": True,
}


def _load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as err:
        print(f"Impossible de lire config.json, utilisation de valeurs par défaut. ({err})")
        return dict(DEFAULT_CONFIG)


_config = _load_config()

# Stats en mémoire, remises à zéro au redémarrage
stats = {
    "started_at": time.time(),
    "guild_count": 0,
    "user_count": 0,
    "commands_used": 0,
    "status": "starting",  # starting | online | offline | error
}

logs = []  # liste de dicts {timestamp, level, message}, du plus récent au plus ancien


def add_log(level: str, message: str) -> dict:
    with _lock:
        entry = {"timestamp": time.time(), "level": level, "message": message}
        logs.insert(0, entry)
        if len(logs) > MAX_LOGS:
            logs.pop()
        return entry


def get_config() -> dict:
    with _lock:
        return dict(_config)


def save_config(updates: dict) -> dict:
    global _config
    with _lock:
        _config.update(updates)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(_config, f, indent=2, ensure_ascii=False)
        return dict(_config)


def increment_commands_used():
    with _lock:
        stats["commands_used"] += 1
