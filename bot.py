import os
import logging
import discord
from discord.ext import commands
from config import DISCORD_TOKEN, MOD_CHANNEL_ID, DELETE_THRESHOLD, FLAG_THRESHOLD, WARN_DM_TEXT, LOG_FILE
from model.predict import predict
from utils.logger import log_event
from utils.report_generator import add_to_report  # ✅ NEW IMPORT

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ PRISM online as {bot.user} (id: {bot.user.id})")
    print("Connected guilds:", [g.name for g in bot.guilds])


def is_admin_member(member: discord.Member, channel: discord.TextChannel):
    try:
        perms = channel.permissions_for(member)
        return perms.manage_messages or perms.kick_members or perms.ban_members or perms.administrator
    except Exception:
        return False


@bot.event
async def on_message(message: discord.Message):
    # Ignore bot messages
    if message.author == bot.user or message.author.bot:
        return

    # Ignore DMs
    if isinstance(message.channel, discord.DMChannel):
        return

    text = message.content or ""
    if not text.strip():
        await bot.process_commands(message)
        return

    try:
        label, prob = predict(text)
    except Exception as e:
        logging.exception("Prediction failed: %s", e)
        await bot.process_commands(message)
        return

    is_admin = is_admin_member(message.author, message.channel)
    action_taken = None

    # 🚨 Delete message if above DELETE_THRESHOLD
    if prob >= DELETE_THRESHOLD and not is_admin:
        try:
            await message.delete()
            action_taken = "deleted"

            try:
                await message.author.send(WARN_DM_TEXT)
            except Exception:
                pass

            await notify_moderators(bot, message, label, prob, action="deleted")

            log_event({
                "action": "deleted",
                "user": str(message.author),
                "user_id": message.author.id,
                "channel": f"{message.guild.name}/{message.channel.name}",
                "content": text,
                "label": label,
                "prob": prob
            })

            # ✅ Add to report dashboard
            add_to_report(
                message.content,
                str(message.author),
                f"{message.guild.name}/{message.channel.name}",
                label,
                prob
            )

        except discord.Forbidden:
            logging.warning("Bot lacks permissions to delete messages in this channel.")
        except Exception as e:
            logging.exception("Failed to delete message: %s", e)

    # ⚠️ Flag message if above FLAG_THRESHOLD
    elif prob >= FLAG_THRESHOLD:
        action_taken = "flagged"
        await notify_moderators(bot, message, label, prob, action="flagged")

        log_event({
            "action": "flagged",
            "user": str(message.author),
            "user_id": message.author.id,
            "channel": f"{message.guild.name}/{message.channel.name}",
            "content": text,
            "label": label,
            "prob": prob
        })

        # ✅ Add to report dashboard
        add_to_report(
            message.content,
            str(message.author),
            f"{message.guild.name}/{message.channel.name}",
            label,
            prob
        )

    await bot.process_commands(message)


async def notify_moderators(bot, message, label, prob, action="flagged"):
    guild = message.guild
    mod_ch_id = MOD_CHANNEL_ID
    summary = (
        f"PRISM {action.upper()} — {label} (p={prob:.2f})\n"
        f"Author: {message.author} ({message.author.id})\n"
        f"Channel: #{message.channel.name}\n"
        f"Message preview: {message.content[:300]}"
    )

    if mod_ch_id and mod_ch_id != 0:
        ch = bot.get_channel(mod_ch_id)
        if ch:
            embed = discord.Embed(title=f"PRISM - {action.upper()}", color=0xff4444)
            embed.add_field(name="Label", value=f"{label} (p={prob:.2f})", inline=False)
            embed.add_field(name="Author", value=f"{message.author} ({message.author.id})", inline=False)
            embed.add_field(name="Channel", value=f"#{message.channel.name}", inline=False)
            embed.add_field(name="Message", value=message.content[:1000] or "<no text>", inline=False)
            await ch.send(embed=embed)
            return

    try:
        owner = guild.owner
        if owner:
            await owner.send(summary)
    except Exception:
        logging.warning("Could not notify mods or owner.")


# --------------------------------------------------------
# ⚙️ MODERATOR COMMANDS
# --------------------------------------------------------

# Command 1: !history — show last N events
@bot.command(name="history")
@commands.has_permissions(manage_messages=True)
async def history(ctx, n: int = 5):
    """
    DMs the last n log lines from logs/prism.log to the requesting moderator.
    Usage: !history or !history 10
    """
    if not os.path.exists(LOG_FILE):
        await ctx.send("No logs found.")
        return

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.read().strip().splitlines()
    except Exception as e:
        await ctx.send(f"Failed to read logs: {e}")
        return

    if not lines:
        await ctx.send("Log file empty.")
        return

    last = lines[-n:]
    out = "\n\n".join(last)

    try:
        await ctx.author.send(f"Last {len(last)} PRISM events:\n\n{out}")
        await ctx.send(f"{ctx.author.mention} I’ve DM’d you the last {len(last)} events.")
    except Exception:
        await ctx.send(f"PRISM events:\n\n{out}")


# Command 2: !dashboard — sends latest HTML dashboard
@bot.command(name="dashboard")
@commands.has_permissions(manage_messages=True)
async def dashboard(ctx):
    """
    Sends the current HTML moderation dashboard to the moderator.
    """
    html_path = os.path.join(os.getcwd(), "report.html")
    if not os.path.exists(html_path):
        await ctx.send("No dashboard found yet — no flagged/deleted messages logged.")
        return

    try:
        await ctx.author.send("📊 Here’s the latest PRISM moderation dashboard:", file=discord.File(html_path))
        await ctx.send(f"{ctx.author.mention} I’ve DM’d you the current moderation dashboard.")
    except Exception:
        await ctx.send(file=discord.File(html_path))


# Global error handler
@history.error
@dashboard.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don’t have permission to use this command.")
    else:
        await ctx.send(f"⚠️ Command error: {error}")


if __name__ == "__main__":
    token = DISCORD_TOKEN
    if not token or token.startswith("PASTE_YOUR_BOT_TOKEN_HERE"):
        print("ERROR: set DISCORD_TOKEN env var or edit config.py")
    else:
        bot.run(token)
