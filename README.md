# Discord Bot + Dashboard (Python)

Bot Discord (discord.py) avec un dashboard web (Flask) pour le monitorer (stats, logs en direct) et le configurer (préfixe, message de bienvenue, couleur des embeds...).

## 1. Créer l'application Discord

1. Va sur https://discord.com/developers/applications et clique **New Application**.
2. Dans l'onglet **Bot** : clique **Reset Token** et copie le token (⚠️ à garder secret).
3. Toujours dans **Bot**, active l'intent **Message Content Intent** et **Server Members Intent**.
4. Dans **OAuth2 > URL Generator** : coche `bot` et `applications.commands`, puis les permissions nécessaires (au minimum `Send Messages`, `Read Message History`, `Embed Links`). Ouvre l'URL générée pour inviter le bot sur ton serveur.

## 2. Installer le projet

```bash
python -m venv venv
source venv/bin/activate   # sous Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Remplis `.env` :

```
DISCORD_TOKEN=le_token_de_ton_bot
PORT=3000
DASHBOARD_TOKEN=choisis-une-chaine-longue-et-secrete
```

## 3. Lancer le bot + dashboard

```bash
python main.py
```

Les commandes slash se synchronisent automatiquement au démarrage (`on_ready`). La première synchronisation globale peut prendre jusqu'à 1h à apparaître sur Discord ; pour du dev rapide sur un seul serveur, tu peux modifier `bot.py` pour utiliser `bot.tree.sync(guild=discord.Object(id=TON_GUILD_ID))`.

Le dashboard est disponible sur **http://localhost:3000**. Connecte-toi avec la valeur de `DASHBOARD_TOKEN`.

## Structure du projet

```
discord-bot-dashboard-py/
├── config.json      # config persistée (modifiable via le dashboard)
├── state.py         # état partagé bot <-> dashboard (thread-safe)
├── bot.py           # client discord.py, événements, commandes slash
├── server.py        # API Flask (stats, logs, config)
├── main.py          # point d'entrée (lance Flask en thread + le bot)
└── public/          # front-end du dashboard (HTML/CSS/JS vanilla)
```

## Fonctionnalités actuelles

- Commandes : `/ping`, `/uptime`, `/say`
- Message de bienvenue automatique sur un salon configurable
- Dashboard :
  - Stats en direct (serveurs, utilisateurs, commandes exécutées, uptime, statut)
  - Logs en direct (rafraîchis toutes les 5s)
  - Formulaire de configuration (préfixe, salon de bienvenue, message, couleur, statut affiché)
  - Protégé par un token simple (`DASHBOARD_TOKEN`)

## Notes techniques

- Flask tourne dans un thread séparé du bot (qui utilise sa propre boucle asyncio) ; l'état partagé (`state.py`) utilise un verrou (`threading.Lock`) pour éviter les accès concurrents.
- Pour de la prod, remplace le serveur de dev Flask par un vrai serveur WSGI (gunicorn, waitress...) et ajoute une authentification plus robuste (OAuth2 Discord).
