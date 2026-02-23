import discord
from discord.ext import commands
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = {}

    def get_balance(self, user_id):
        return self.balances.get(user_id, 100)

    def update_balance(self, user_id, amount):
        current = self.get_balance(user_id)
        self.balances[user_id] = current + amount

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx, member: discord.Member = None):
        """Check your or another user's balance."""
        member = member or ctx.author
        balance = self.get_balance(member.id)
        embed = discord.Embed(title="Economy", description=f"{member.display_name}'s balance: **{balance}** coins", color=discord.Color.gold())
        await ctx.send(embed=embed)

    @commands.command(name="work")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        """Work to earn some coins."""
        earnings = random.randint(50, 150)
        self.update_balance(ctx.author.id, earnings)
        await ctx.send(f"💰 You worked hard and earned **{earnings}** coins!")

    @commands.command(name="gamble")
    async def gamble(self, ctx, amount: int):
        """Gamble your coins. Double or nothing!"""
        if amount <= 0:
            await ctx.send("❌ Please enter a positive amount.")
            return

        balance = self.get_balance(ctx.author.id)
        if amount > balance:
            await ctx.send("❌ You don't have enough coins!")
            return

        if random.random() > 0.5:
            self.update_balance(ctx.author.id, amount)
            await ctx.send(f"🎉 You won! You now have **{self.get_balance(ctx.author.id)}** coins.")
        else:
            self.update_balance(ctx.author.id, -amount)
            await ctx.send(f"😢 You lost **{amount}** coins. Better luck next time!")

async def setup(bot):
    await bot.add_cog(Economy(bot))