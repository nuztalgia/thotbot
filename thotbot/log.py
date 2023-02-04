import logging
import sys
from typing import Final

from botstrap import Color

logging.basicConfig(
    level=logging.DEBUG,
    style="{",
    format=Color.pink("[{asctime}]") + " {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

for logger_name in ["asyncio", "discord"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


class Log:
    _logger: Final[logging.Logger] = logging.getLogger(__name__)

    @classmethod
    def d(cls, message: str) -> None:
        cls._logger.debug(Color.grey(message))

    @classmethod
    def i(cls, message: str) -> None:
        cls._logger.info(message)

    @classmethod
    def w(cls, message: str) -> None:
        cls._logger.warning(Color.yellow(f"WARNING: {message}"))

    @classmethod
    def e(cls, message: str) -> None:
        cls._logger.error(Color.red(f"ERROR: {message}"))
