from functools import cached_property
from pathlib import Path
from typing import Any, Final

from botstrap import Color
from discord import Bot, Forbidden, Guild, Intents, User
from discord.abc import GuildChannel
from discord.commands import ApplicationContext

from thotbot import utils
from thotbot.config import Config
from thotbot.log import Log


# noinspection PyDunderSlots, PyUnresolvedReferences
def _get_required_intents() -> Intents:
    intents = Intents.default()
    intents.members = True
    intents.message_content = True
    return intents


# noinspection PyAbstractClass
class ThotBot(Bot):
    def __init__(self, force_sync: bool, **options: Any) -> None:
        super().__init__(
            intents=_get_required_intents(),
            owner_id=Config.owner_id,
            **options,
        )

        self.owner: User = self.get_user(self.owner_id)
        self.home_guild: Guild = self.get_guild(Config.home_guild_id)
        self.known_channels: Final[dict[str, GuildChannel]] = {}

        self._force_sync: Final[bool] = force_sync
        self._initialized: bool = False

        for file_path in Path(__file__).parent.glob("cogs/[!_]*.py"):
            Log.d(f"Loading extension '{file_path.stem}'.")
            self.load_extension(f"thotbot.cogs.{file_path.stem}")

    @cached_property
    def color_value(self) -> int:
        color = utils.get_color_value(Config.accent_color)
        if color != utils.NO_COLOR:
            return color
        elif accent_color := self.user.accent_color:
            return accent_color.value
        else:
            return utils.NO_COLOR

    def log_attributes(self, prefix: str = "  - ") -> None:
        loggable_home_guild = self.home_guild.name + Color.grey(
            f" (Members: {self.home_guild.approximate_member_count})"
        )
        loggable_channels = utils.dict_to_str(
            self.known_channels, utils.get_channel_loggable_name
        )

        for attribute_name, attribute_value in [
            ("Owner", self.owner),
            ("Home Guild", loggable_home_guild),
            ("Known Channels", loggable_channels),
        ]:
            Log.i(f"{Color.cyan(f'{prefix}{attribute_name}:')} {attribute_value}")

        Log.d("Finished logging bot attributes.")

    # noinspection PyPropertyAccess, PyProtectedMember
    async def make_fetch_happen(self) -> None:
        if self._initialized:
            Log.d(f"Reloading config from '{Config._file_path}'.")
            Config.reload_from_file()
            try:
                del self.color_value  # Invalidate the cached property.
            except AttributeError:
                pass  # The property wasn't cached. Nothing to delete.
        else:
            Log.d(f"Loaded config from '{Config._file_path}'.")

        if self._initialized or not self.owner:
            Log.d("Fetching bot owner user.")
            self.owner = await self.get_or_fetch_user(self.owner_id)
            await self.owner.create_dm()

        if self._initialized or not self.home_guild:
            Log.d("Fetching home guild/server.")
            self.home_guild = await self.fetch_guild(Config.home_guild_id)

        self.known_channels.clear()
        for channel_key, channel_id in Config.channels.items():
            await self._cache_channel(channel_key, channel_id)

    async def _cache_channel(self, channel_key: str, channel_id: int) -> None:
        try:
            if self._initialized or not (channel := self.get_channel(channel_id)):
                Log.d(f"Fetching known channel '{channel_key}'.")
                channel = await self.fetch_channel(channel_id)
            self.known_channels[channel_key] = channel
        except Forbidden:
            Log.w(f"Missing access to channel '{channel_key}'.")

    # noinspection PyMethodMayBeStatic
    async def on_application_command(self, ctx: ApplicationContext) -> None:
        command_name = ctx.command.qualified_name
        channel_name = utils.get_channel_loggable_name(ctx.channel)
        Log.i(f"{ctx.user} used command '{command_name}' in {channel_name}.")

    async def on_ready(self) -> None:
        if self._initialized:
            Log.i("Received another 'on_ready' event. Ignoring.")
            return

        if self._force_sync:
            Log.w("Force-syncing commands. Be mindful of the rate limit.")
            await self.sync_commands(force=True)

        await self.make_fetch_happen()
        self._initialized = True

        Log.i("ThotBot is online and ready!")
        self.log_attributes()
