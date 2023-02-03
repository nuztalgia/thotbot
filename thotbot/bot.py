from typing import Any

from discord import Bot, Intents


# noinspection PyDunderSlots, PyUnresolvedReferences
def _get_required_intents() -> Intents:
    intents = Intents.default()
    intents.members = True
    intents.message_content = True
    return intents


# noinspection PyAbstractClass
class ThotBot(Bot):
    def __init__(self, force_sync: bool, **options: Any) -> None:
        super().__init__(intents=_get_required_intents(), **options)
