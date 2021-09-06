from typing import List
from typing import Union

from pyrogram import filters


def command(commands: Union[str, List[str]]):
    return filters.command(commands)
