from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
import json
import os
import random
import time
from datetime import datetime, timedelta

class Economy8Afc1FCog(commands.Cog):
    """SwanEconomy: A sophisticated economy system with market fluctuations."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_path = "economy_data.json"
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_data(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def _get_user_data(self, user_id: str):
        if user_id not in self.data:
            self.data[user_id] = {
                "wallet": 1000,
                "bank": 0,
                "last_work": 0,
                "name": ""
            }
        return self.data[user_id]

    def _get_market_multiplier(self) -> tuple[float, str]:
        # Simulates market state: Recession, Stable, Bull Market, Boom
        states = [
            (0.5, "不況 (Recession)"),
            (1.0, "安定 (Stable)"),
            (1.5, "好景気 (Bull Market)"),
            (2.5, "バブル (Boom)")
        ]
        return random.choices(states, weights=[20, 50, 20, 10])[0]

    def _get_rank(self, total: int) -> tuple[str, int]:
        if total < 5000:
            return "ブロンズ市民", 0xcd7f32
        elif total < 20000:
            return "シルバー市民", 0xc0c0c0
        elif total < 100000:
            return "ゴールド投資家", 0xffd700
        elif total < 500000:
            return "プラチナ実業家", 0xe5e4e2
        else:
            return "スワン大富豪", 0x00ffff

    @app_commands.command(name="work", description="仕事をして報酬を得ます。景気によって報酬が変動します。")
    async def work(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_data = self._get_user_data(user_id)
        
        current_time = time.time()
        cooldown_seconds = 3600 # 1 hour
        
        if current_time - user_data.get("last_work", 0) < cooldown_seconds:
            remaining = int(cooldown_seconds - (current_time - user_data["last_work"]))
            minutes = remaining // 60
            return await interaction.response.send_message(
                f"休憩が必要です。あと {minutes} 分待ってください。", ephemeral=True
            )

        multiplier, market_name = self._get_market_multiplier()
        base_reward = random.randint(100, 500)
        final_reward = int(base_reward * multiplier)

        user_data["wallet"] += final_reward
        user_data["last_work"] = current_time
        user_data["name"] = interaction.user.display_name
        self._save_data()

        embed = discord.Embed(
            title="💼 仕事完了",
            description=f"一生懸命働いて **{final_reward}** スワンコインを稼ぎました！",
            color=discord.Color.green()
        )
        embed.add_field(name="現在の景気", value=market_name, inline=True)
        embed.add_field(name="基本給", value=f"{base_reward}", inline=True)
        embed.add_field(name="倍率", value=f"x{multiplier}", inline=True)
        embed.set_footer(text=f"現在の所持金: {user_data['wallet']}コイン")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="wallet", description="現在の所持金、銀行残高、および資産ランクを確認します。")
    @app_commands.describe(user="確認したいユーザー（省略した場合は自分）")
    async def wallet(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target = user or interaction.user
        user_id = str(target.id)
        user_data = self._get_user_data(user_id)
        
        wallet = user_data["wallet"]
        bank = user_data["bank"]
        total = wallet + bank
        rank_name, rank_color = self._get_rank(total)

        embed = discord.Embed(
            title=f"💰 {target.display_name} の資産状況",
            color=rank_color
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="財布", value=f"{wallet:,} コイン", inline=True)
        embed.add_field(name="銀行", value=f"{bank:,} コイン", inline=True)
        embed.add_field(name="合計資産", value=f"{total:,} コイン", inline=False)
        embed.add_field(name="資産ランク", value=rank_name, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bank", description="銀行への預け入れ、または引き出しを行います。")
    @app_commands.rename("withdraw"]="withdraw")
    @app_commands.describe(action="預け入れ(deposit)か引き出し(withdraw)を選択", amount="操作する金額")
    async def bank(self, interaction: discord.Interaction, action: Literal["deposit", "withdraw"], amount: int):
        if amount <= 0:
            return await interaction.response.send_message("金額は1以上の数値を指定してください。", ephemeral=True)

        user_id = str(interaction.user.id)
        user_data = self._get_user_data(user_id)

        if action == "deposit":
            if user_data["wallet"] < amount:
                return await interaction.response.send_message("財布に十分な現金がありません。", ephemeral=True)
            user_data["wallet"] -= amount
            user_data["bank"] += amount
            msg = f"銀行に **{amount:,}** コインを預け入れました。"
        else:
            if user_data["bank"] < amount:
                return await interaction.response.send_message("銀行残高が不足しています。", ephemeral=True)
            user_data["bank"] -= amount
            user_data["wallet"] += amount
            msg = f"銀行から **{amount:,}** コインを引き出しました。"

        self._save_data()
        
        embed = discord.Embed(
            title="🏦 銀行取引完了",
            description=msg,
            color=discord.Color.blue()
        )
        embed.add_field(name="現在の財布", value=f"{user_data['wallet']:,}", inline=True)
        embed.add_field(name="現在の銀行", value=f"{user_data['bank']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pay", description="他のユーザーにお金を送金します。")
    @app_commands.describe(receiver="送金先のユーザー", amount="送金する金額")
    async def pay(self, interaction: discord.Interaction, receiver: discord.Member, amount: int):
        if receiver.id == interaction.user.id:
            return await interaction.response.send_message("自分自身に送金することはできません。", ephemeral=True)
        
        if receiver.bot:
            return await interaction.response.send_message("Botに送金することはできません。", ephemeral=True)

        if amount <= 0:
            return await interaction.response.send_message("送金額は1以上の数値を指定してください。", ephemeral=True)

        sender_id = str(interaction.user.id)
        receiver_id = str(receiver.id)
        
        sender_data = self._get_user_data(sender_id)
        receiver_data = self._get_user_data(receiver_id)

        if sender_data["wallet"] < amount:
            return await interaction.response.send_message("財布の残高が不足しています。", ephemeral=True)

        sender_data["wallet"] -= amount
        receiver_data["wallet"] += amount
        
        self._save_data()

        embed = discord.Embed(
            title="💸 送金完了",
            description=f"{interaction.user.mention} が {receiver.mention} に送金しました。",
            color=discord.Color.gold()
        )
        embed.add_field(name="送金額", value=f"{amount:,} コイン", inline=False)
        embed.set_footer(text="SwanEconomy P2P Transfer")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy8Afc1FCog(bot))
# === END FILE ===