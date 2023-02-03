from importlib.metadata import version

from botstrap import Botstrap, CliColors, Color, Option
from discord import Activity, ActivityType


def main() -> int:
    botstrap = (
        Botstrap(
            name := "thotbot",
            version=version(name),
            colors=CliColors(primary=Color.pink),
        )
        .register_token(
            uid="dev",
            display_name=Color.yellow("development"),
        )
        .register_token(
            uid="prod",
            requires_password=True,
            display_name=Color.green("production"),
        )
    )
    args = botstrap.parse_args(
        force_sync=Option(flag=True, help="Force-sync all ThotBot app commands."),
    )
    botstrap.run_bot(
        bot_class="thotbot.bot.ThotBot",
        activity=Activity(type=ActivityType.listening, name="your thots."),
        force_sync=args.force_sync,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
