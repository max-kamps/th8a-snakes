import traceback as tb
import discord.ext.commands as cmd
import importlib

from helper.common import *


nl = '\n'


class ExtUtilCog(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmd.group(hidden=True, invoke_without_command=True)
    @is_superuser()
    async def ext(self, ctx):
        await ctx.send(f'```Loaded extensions:\n{nl.join(self.bot.extensions)}```')

    @ext.command(name='reload_all')
    @is_superuser()
    async def cmd_reload_all(self, ctx):
        success = True
        for extension in self.bot.extensions.copy():
            self.bot.unload_extension(extension)
            importlib.reload(__import__(extension))

            try:
                self.bot.load_extension(extension)
            except Exception:
                success = False
                tb.print_exc()

        await ctx.add_success_reaction(success)

    @ext.command(name='load')
    @is_superuser()
    async def cmd_load(self, ctx, extension: str):
        if extension in self.bot.extensions:
            self.bot.unload_extension(extension)
            importlib.reload(__import__(extension))

        try:
            self.bot.load_extension(extension)
        except Exception:
            await ctx.add_success_reaction(False)
            tb.print_exc()
        else:
            await ctx.add_success_reaction(True)

    @ext.command(name='unload')
    @is_superuser()
    async def cmd_unload(self, extension: str):
        if extension == 'all':
            for extension in self.bot.extensions.copy():
                self.bot.unload_extension(extension)

        if extension not in self.bot.extensions: return
        self.bot.unload_extension(extension)


def setup(bot):
    bot.add_cog(ExtUtilCog(bot))
