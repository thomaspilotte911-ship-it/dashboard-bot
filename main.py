import os
import threading

from dotenv import load_dotenv

load_dotenv()

import state
from server import create_app
from bot import bot


def run_flask():
    app = create_app()
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)


def main():
    token = os.environ.get("DISCORD_TOKEN")
    dashboard_token = os.environ.get("DASHBOARD_TOKEN")

    if not token:
        raise SystemExit("❌ DISCORD_TOKEN manquant. Copie .env.example vers .env et remplis-le.")
    if not dashboard_token:
        raise SystemExit("❌ DASHBOARD_TOKEN manquant dans .env.")

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"🌐 Dashboard disponible sur http://localhost:{os.environ.get('PORT', 3000)}")

    try:
        bot.run(token)
    except Exception as err:
        state.stats["status"] = "error"
        state.add_log("error", f"Échec de connexion à Discord: {err}")
        raise


if __name__ == "__main__":
    main()
