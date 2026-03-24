import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from hercai import Hercai
import g4f

# Load Environment Variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize Free Image Engine
herc = Hercai()

class CodeWeaver(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"🚀 Code Weaver is online as {self.user}")

bot = CodeWeaver()

# --- 1. CHAT & CODING (/chat) ---
@bot.tree.command(name="chat", description="Free AI Chat - Great for Coding")
async def chat(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    try:
        response = await asyncio.to_thread(
            g4f.ChatCompletion.create,
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
        )
        await interaction.followup.send(f"**AI:**\n{response[:1990]}")
    except Exception:
        await interaction.followup.send("❌ Engine busy. Try again.")

# --- 2. IMAGE (/draw) ---
@bot.tree.command(name="draw", description="Generate a free AI image")
async def draw(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    result = await asyncio.to_thread(herc.draw_image, model="v3", prompt=prompt)
    url = result.get("url")
    if url:
        embed = discord.Embed(title="🎨 Code Weaver Canvas", description=f"Prompt: `{prompt}`", color=0x00ffcc)
        embed.set_image(url=url)
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Image server offline.")

# --- 3. VIDEO (/video) ---
@bot.tree.command(name="video", description="Generate a free motion clip")
async def video(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    result = await asyncio.to_thread(herc.draw_image, model="v3", prompt=f"animated gif, motion, {prompt}")
    await interaction.followup.send(f"🎥 **Motion Clip:**\n{result.get('url')}")

# --- 4. CLEAR (/clear) ---
@bot.tree.command(name="clear", description="Delete messages (up to 1000)")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.send_message(f"🧹 Clearing {amount} messages...", ephemeral=True)
    deleted = 0
    while deleted < amount:
        to_delete = min(amount - deleted, 100)
        purged = await interaction.channel.purge(limit=to_delete)
        deleted += len(purged)
        if len(purged) == 0: break
        await asyncio.sleep(1)
    await interaction.channel.send(f"✅ Cleared {deleted} messages.", delete_after=5)

# --- 5. RADIO 24/7 (/radio) ---
@bot.tree.command(name="radio", description="Play 24/7 Lofi Radio")
async def radio(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You must be in a voice channel!")
        return

    await interaction.response.defer()
    channel = interaction.user.voice.channel
    
    # Lofi Girl Radio Stream URL
    url = "https://lofi.stream.laut.fm/lofi" 

    try:
        # Connect to voice
        if interaction.guild.voice_client is None:
            vc = await channel.connect()
        else:
            vc = interaction.guild.voice_client

        # Play audio
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(url))
            await interaction.followup.send(f"📻 **Radio Started!** Joined `{channel.name}`. I will stay here 24/7.")
        else:
            await interaction.followup.send("📻 Radio is already playing!")
            
    except Exception as e:
        print(f"Radio Error: {e}")
        await interaction.followup.send("❌ Could not start radio. Ensure the bot has Voice permissions and FFmpeg is installed.")

@bot.tree.command(name="stop_radio", description="Stop the radio and leave")
async def stop_radio(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 Radio stopped. Bye!")
    else:
        await interaction.response.send_message("❌ I'm not in a voice channel.")

if __name__ == "__main__":
    bot.run(TOKEN)