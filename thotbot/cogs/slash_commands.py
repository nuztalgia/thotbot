from typing import Final

from discord import ApplicationContext, Cog
from discord.commands import slash_command

from thotbot import Log, ThotBot, utils


async def _respond_with_gif(ctx: ApplicationContext, file_name: str) -> None:
    await utils.edit_or_respond(ctx, file=utils.get_asset_file(f"{file_name}.gif"))


class SlashCommands(Cog):
    def __init__(self, bot: ThotBot) -> None:
        self.bot: Final[ThotBot] = bot

    @slash_command(description="Make fetch happen.")
    async def fetch(self, ctx: ApplicationContext) -> None:
        if ctx.user.id != self.bot.owner_id:
            await _respond_with_gif(ctx, "stop-trying-to-make-fetch-happen")
            Log.d("Will not proceed with 'fetch' command from an unauthorized user.")
            return

        await ctx.response.defer(invisible=False)
        Log.d("Triggering a re-fetch of all custom bot attributes.")
        await self.bot.make_fetch_happen()

        await _respond_with_gif(ctx, "that-is-so-fetch")
        Log.i("Successfully re-fetched all custom bot attributes.")
        self.bot.log_attributes()


def setup(bot: ThotBot) -> None:
    bot.add_cog(SlashCommands(bot))
