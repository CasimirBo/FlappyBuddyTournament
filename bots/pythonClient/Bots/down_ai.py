from Bots.bot_ai import BotAI
from Bots.data import PlayState


class DownAI(BotAI):
    fly = True

    def _play_impl(self, current_game_state: PlayState):

        self.fly = False
        return self.fly

    def get_name(self):
        return self.name

    def __init__(self):
        # todo: give your bot a super duper cool name
        self.name = "AlwaysDown"
