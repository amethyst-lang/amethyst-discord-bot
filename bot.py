import os
import subprocess

import discord
from discord.ext import commands
import dotenv

bot = commands.Bot(command_prefix="a!", activity=discord.Game(name='Amethyst Lang'))
dotenv.load_dotenv()

@bot.command()
async def ping(ctx):
    await ctx.reply("pong")

@bot.command()
async def run(ctx):
    code = '\n'.join(ctx.message.content.split('```')[1:][::2]).strip()

    if code == '':
        await ctx.reply('Encase Amethyst code with a code block')
    else:
        async with ctx.typing():
            filename = 'exe_%i' % ctx.message.id
            child = subprocess.run(['./bin/amethyst', '/dev/stdin', filename], input=code, text=True, capture_output=True)
            if child.returncode != 0:
                await ctx.reply(embed=discord.Embed(title='Error encountered when compiling', description='```ansi\n%s\n```' % child.stderr, colour=0xff0000))
            else:
                try:
                    child = subprocess.run(['./' + filename], text=True, capture_output=True, timeout=10)
                    embed = discord.Embed(title='Process ended with error code `%i`' % child.returncode, colour=0x00ff00)
                    if child.stdout:
                        embed.add_field(name='STDOUT', value='```ansi\n%s\n```' % child.stdout.replace('`', "'"), inline=False)
                    if child.stderr:
                        embed.add_field(name='STDERR', value='```ansi\n%s\n```' % child.stderr.replace('`', "'"), inline=False)
                    await ctx.reply(embed=embed)
                except subprocess.TimeoutExpired:
                    await ctx.reply(embed=discord.Embed(title='Process timed out', colour=0x0000ff))
                os.remove(filename)
                os.remove(filename + '.o')

bot.run(os.getenv("TOKEN"))
