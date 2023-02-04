import json
import re
from collections.abc import Callable
from functools import partial
from typing import Any, Final

import emoji
from discord import ChannelType, Color, Member, User
from discord.abc import GuildChannel

NO_COLOR: Final[int] = -1

_sanitize_channel_name: Final[Callable[[str], str]] = partial(
    re.compile(r"(:[\w-]+:|^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$)", re.ASCII).sub, ""
)


def dict_to_str(
    data: dict[str, Any],
    value_to_string: Callable[[Any], str] = str,
    regular_indent: int = 4,
    newline_indent: int = 26,
) -> str:
    return json.dumps(
        {key: value_to_string(value) for key, value in data.items()},
        indent=regular_indent,
    ).replace("\n", f"\n{' ' * newline_indent}")


def get_channel_display_name(
    channel: GuildChannel,
    user: Member | User | None,
    *,
    allow_mention: bool = True,
    bold_text: bool = True,
) -> str:
    if user and allow_mention:
        mutual_guild_ids = [guild.id for guild in user.mutual_guilds]
        if channel.guild.id in mutual_guild_ids:
            return channel.mention

    sanitized_name = _sanitize_channel_name(emoji.demojize(channel.name))
    display_name = f"#{sanitized_name}" if sanitized_name else f"Channel #{channel.id}"
    return f"**{display_name}**" if bold_text else display_name


def get_channel_loggable_name(channel: GuildChannel) -> str:
    if channel.type == ChannelType.private:
        return "a direct message"
    else:
        return get_channel_display_name(
            channel, user=None, allow_mention=False, bold_text=False
        )


def get_color_value(color: str) -> int:
    color = re.sub(r"\W", "", color.lower(), re.ASCII)

    if color in ["", "default", "embed_background"]:
        return NO_COLOR
    elif hasattr(Color, color):
        return getattr(Color, color).value
    else:
        return min(abs(int(color, 16)), 0xFFFFFF)
