import time
import discord
from discord import app_commands
from discord.ext import commands

import state

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def refresh_guild_stats():
    state.stats["guild_count"] = len(bot.guilds)
    state.stats["user_count"] = sum(g.member_count or 0 for g in bot.guilds)


def _embed_color(cfg: dict) -> int:
    try:
        return int(cfg.get("embedColor", "#5865F2").lstrip("#"), 16)
    except ValueError:
        return 0x5865F2


def _log_command(interaction: discord.Interaction, name: str):
    state.increment_commands_used()
    cfg = state.get_config()
    if cfg.get("logCommandUsage", True):
        guild_name = interaction.guild.name if interaction.guild else "DM"
        state.add_log("info", f'/{name} utilisée par {interaction.user} sur "{guild_name}"')


@bot.event
async def on_ready():
    state.stats["status"] = "online"
    refresh_guild_stats()

    cfg = state.get_config()
    await bot.change_presence(activity=discord.Game(name=cfg.get("botStatus", "")))

    state.add_log("success", f"Bot connecté en tant que {bot.user}")

    try:
        synced = await bot.tree.sync()
        state.add_log("info", f"{len(synced)} commande(s) slash synchronisée(s)")
    except Exception as err:
        state.add_log("error", f"Échec de synchronisation des commandes: {err}")


@bot.event
async def on_guild_join(guild: discord.Guild):
    refresh_guild_stats()
    state.add_log("info", f'Ajouté au serveur "{guild.name}" ({guild.member_count} membres)')


@bot.event
async def on_guild_remove(guild: discord.Guild):
    refresh_guild_stats()
    state.add_log("warning", f'Retiré du serveur "{guild.name}"')


@bot.event
async def on_member_join(member: discord.Member):
    cfg = state.get_config()
    channel_id = cfg.get("welcomeChannelId")
    if not channel_id:
        return

    try:
        channel = member.guild.get_channel(int(channel_id))
    except (TypeError, ValueError):
        channel = None
    if not channel:
        return

    text = cfg.get("welcomeMessage", "Bienvenue {user} !").replace("{user}", member.mention)
    embed = discord.Embed(description=text, color=_embed_color(cfg))
    try:
        await channel.send(embed=embed)
    except Exception as err:
        state.add_log("error", f"Échec d'envoi du message de bienvenue: {err}")


@bot.event
async def on_error(event_method, *args, **kwargs):
    state.stats["status"] = "error"
    state.add_log("error", f"Erreur dans {event_method}")


@bot.tree.command(name="ping", description="Vérifie la latence du bot")
async def ping(interaction: discord.Interaction):
    _log_command(interaction, "ping")
    await interaction.response.send_message(f"🏓 Pong ! Latence: {round(bot.latency * 1000)}ms")


@bot.tree.command(name="uptime", description="Affiche depuis combien de temps le bot tourne")
async def uptime(interaction: discord.Interaction):
    _log_command(interaction, "uptime")
    seconds = int(time.time() - state.stats["started_at"])
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    await interaction.response.send_message(f"⏱️ En ligne depuis {h}h {m}m {s}s")


@bot.tree.command(name="say", description="Fait dire quelque chose au bot")
@app_commands.describe(message="Le message à envoyer")
async def say(interaction: discord.Interaction, message: str):
    _log_command(interaction, "say")
    cfg = state.get_config()
    embed = discord.Embed(description=message, color=_embed_color(cfg))
    await interaction.response.send_message(embed=embed)
