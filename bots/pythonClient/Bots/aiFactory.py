from Bots.bot_ai import BotAI
from Bots.first_ai import FirstAI
from Bots.up_ai import UpAI
from Bots.down_ai import DownAI
from Bots.collision_avoidance import ColAvoidAI
from Bots.force_ai import ForceAI
from Bots.force2_ai import Force2AI

ai_bots = {
    "FirstAI": FirstAI,
    "UpAI": UpAI,
    "DownAI": DownAI,
    "ColAvoidAI": ColAvoidAI,
    "ForceAI": ForceAI,
    "Force2AI": Force2AI
}


def ai_factory(bot_selection="FirstAI") -> BotAI:
    return ai_bots[bot_selection]()
