from __future__ import annotations

import os
import asyncio
import logging

import discord
from discord.ext import commands
from keep_alive import keep_alive

# === ロギング設定 ===
# Botの動作状況をコンソールに出力するための設定です
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === インテントの設定 ===
# Botが受け取る情報の種類を指定します
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Botクラスのインスタンス化
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready() -> None:
    """Botがオンラインになった時に実行されるイベント"""
    logger.info(f"{bot.user.name} (ID: {bot.user.id}) が起動しました！")
    try:
        # スラッシュコマンドをDiscord側に同期します
        synced = await bot.tree.sync()
        logger.info(f"スラッシュコマンド {len(synced)}個 を同期しました")
    except Exception as e:
        logger.error(f"コマンド同期エラー: {e}")

async def load_cogs() -> None:
    """cogsフォルダ内のファイルを読み込みます"""
    # cogs/ フォルダ内の .py ファイルを走査
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded cog: {filename}")
            except Exception as e:
                logger.error(f"Failed to load {filename}: {e}")

async def main() -> None:
    """メインの実行関数"""
    # Koyebなどの常時起動用Webサーバーを開始
    keep_alive()
    
    # Cogの読み込み
    await load_cogs()
    
    # 環境変数からトークンを取得してBotを起動
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN が設定されていません。.envファイルを確認してください。")
        return
    
    async with bot:
            try:
        await bot.load_extension("cogs.doctor")
    except Exception:
        pass  # doctor cog is optional
    await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # 手動停止時のエラー出力を抑制
        pass