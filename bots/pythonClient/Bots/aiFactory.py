from Bots.bot_ai import BotAI
from Bots.first_ai import FirstAI
from Bots.up_ai import UpAI
from Bots.down_ai import DownAI

ai_bots = {
    "FirstAI": FirstAI,
    "UpAI": UpAI,
    "DownAI": DownAI,
}


def ai_factory(bot_selection="FirstAI") -> BotAI:
    return ai_bots[bot_selection]()
