import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

MAX_SIZE = 50 
log_queue = asyncio.Queue(maxsize=MAX_SIZE)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.command(name="logs")
async def get_logs(ctx, count: int = 10):
    logs = []
    for _ in range(min(count, log_queue.qsize())):
        logs.append(await log_queue.get())
    if logs:
        await ctx.send("***********************************************************\nLogs:\n" + "\n".join(logs))
    else:
        await ctx.send("No logs available.")

def start_bot(token):
    try:
        bot.run(token)
    except:
        print("Can't connect to bot at the moment")

async def push_log(log_message):
    if log_queue.full():
        await log_queue.get()  
    await log_queue.put(log_message)
