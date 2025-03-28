from abc import abstractmethod, ABC
import json
import os
from datetime import datetime

from Bots.data import PlayState

class BotAI(ABC):

    name = "BotAI"
    play_scores = []
    start_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Timestamp when the bot starts

    def dump_scores_to_json(self):
        data = {
            "start_time": self.start_time,
            "play_scores": self.play_scores
        }
        # Ensure the directory exists
        directory = f"data/{self.name}"
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
        
        with open(f"{directory}/play_scores_{self.start_time}.json", "w") as json_file:
            json.dump(data, json_file, indent=4)


    def play(self, current_game_state: PlayState):
        # Shared functionality for all implementations
        print(current_game_state.player.state)

        # Handle end of game states
        if current_game_state.player.state == "finished" or current_game_state.player.state == "died":
            print(f"Level finished. Score of {current_game_state.score} was added to list.")
            self.play_scores.append({"score":current_game_state.score,"player_state":current_game_state.player.state})
            self.dump_scores_to_json()


        
        # Call the specific implementation of play
        return self._play_impl(current_game_state)
    



            



    @abstractmethod
    def _play_impl(self, current_game_state):
        pass

    @abstractmethod
    def get_name(self):
        pass
