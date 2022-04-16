import os
import shutil
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
            d = 'msg_%i' % ctx.message.id
            os.mkdir(d)
            filename = '%s/a.out' % d
            child = subprocess.run(['./bin/amethyst', '/dev/stdin', filename], input=code, text=True, capture_output=True)
            if child.returncode != 0:
                await ctx.reply(embed=discord.Embed(title='Error encountered when compiling', description='```ansi\n%s\n```' % child.stderr, colour=0xff0000))
                shutil.rmtree(d)
            else:
                shutil.copy('Dockerfile', d)
                try:
                    subprocess.run(['docker', 'build', '-t', '%s:latest' % d, d])
                    child = subprocess.run(['docker', 'run', d], text=True, capture_output=True, timeout=10)
                    embed = discord.Embed(title='Process ended with error code `%i`' % child.returncode, colour=0x00ff00)
                    if child.stdout:
                        embed.add_field(name='STDOUT', value='```ansi\n%s\n```' % child.stdout.replace('`', "'"), inline=False)
                    if child.stderr:
                        embed.add_field(name='STDERR', value='```ansi\n%s\n```' % child.stderr.replace('`', "'"), inline=False)
                    await ctx.reply(embed=embed)
                except subprocess.TimeoutExpired:
                    await ctx.reply(embed=discord.Embed(title='Process timed out', colour=0x0000ff))
                finally:
                    shutil.rmtree(d)
                    subprocess.run(['docker', 'image', 'rm', '--force', d])

bot.run(os.getenv("TOKEN"))
