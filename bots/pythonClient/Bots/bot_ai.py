from abc import abstractmethod, ABC
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg


from Bots.data import PlayState



class BotAI(ABC):
    last_score = 0

    name = "BotAI"
    play_scores = []
    start_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Timestamp when the bot starts


    # Own visualization
    app = QApplication([])  # Use QApplication from QtWidgets
    win = pg.GraphicsLayoutWidget(show=True, title="Live 2D Data Points")
    win.show()
    plot = win.addPlot(title="Live Data", row=0, col=0)
    plot.showGrid(x=True, y=True)  # Enable grid lines
    plot.setXRange(0, 768)  # Fixed x-axis range
    plot.setYRange(0, 512)  # Fixed y-axis range
    legend = pg.LegendItem()       # Create the legend item
    win.addItem(legend, row=0, col=1)
    
    player_position_scatter = pg.ScatterPlotItem(pen=None, symbol='o', size=10, brush='#FF9100FF')
    plot.addItem(player_position_scatter)
    legend.addItem(player_position_scatter, "Player")

    coin_position_scatter = pg.ScatterPlotItem(pen=None, symbol='o', size=10, brush='y')
    plot.addItem(coin_position_scatter)
    legend.addItem(coin_position_scatter, "Coin")

    seagull_position_scatter = pg.ScatterPlotItem(pen=None, symbol='o', size=10, brush='g')
    plot.addItem(seagull_position_scatter)
    legend.addItem(seagull_position_scatter, "Seagull")

    raven_position_scatter = pg.ScatterPlotItem(pen=None, symbol='o', size=10, brush='b')
    plot.addItem(raven_position_scatter)
    legend.addItem(raven_position_scatter, "Raven")

    

    def dump_scores_to_json(self, current_score, level_time):
        data = {
            "start_time": self.start_time,
            "play_scores": self.play_scores
        }
        # Ensure the directory exists
        directory = f"data/{self.name}"
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
        
        with open(f"{directory}/play_scores_{self.start_time}.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

        data = {"play_scores": current_score,"play_time":level_time}
        with open(f"current_Score.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

        # v2
        with open("./opt_data/folder_info.json", "r") as json_file:
            data = json.load(json_file)
            v2_output_file = data.get("output_file", 0.0)

        if os.path.exists(v2_output_file):
            with open(v2_output_file, "r") as json_file:
                data_scores = json.load(json_file)
                v2_scores = data_scores.get("scores", [])
                v2_times = data_scores.get("times", [])
        else:
            v2_scores = []
            v2_times = []

        v2_scores.append(current_score)
        v2_times.append(level_time)

        output_dir = os.path.dirname(v2_output_file)
        os.makedirs(output_dir, exist_ok=True)  # This creates the necessary folders if they don't exist

        # Write the updated scores back to the file
        with open(v2_output_file, "w") as json_file:
            # You might want to structure the data more than just appending to `scores`
            json.dump({"scores": v2_scores,"times":v2_times}, json_file, indent=4)

    def visualize_positions(self, current_game_state: PlayState):

        # Update Player position
        self.player_position_scatter.setData([{'pos': (current_game_state.player.pos_x, current_game_state.player.pos_y)}])

        # Update Coin positions
        coins =  []
        seagull = []
        raven = []
        for obstacle in current_game_state.obstacles:
            if obstacle.type == "Coin":
                coins.append({'pos': (obstacle.origin_x, obstacle.origin_y)})
            elif obstacle.type == "Seagull":
                seagull.append({'pos': (obstacle.origin_x, obstacle.origin_y)})
            elif obstacle.type == "Raven":
                raven.append({'pos': (obstacle.origin_x, obstacle.origin_y)})

        self.coin_position_scatter.setData(coins)
        self.seagull_position_scatter.setData(seagull)
        self.raven_position_scatter.setData(raven)
        self.app.processEvents()

    def play(self, current_game_state: PlayState):
        # Shared functionality for all implementations

        # Handle end of game states
        if current_game_state.player.state == "finished":
            print(f"Level finished. Score of {current_game_state.score} was added to list.")
            self.play_scores.append({"score":current_game_state.score,"player_state":current_game_state.player.state})
            self.dump_scores_to_json(current_game_state.score, current_game_state.level_time)
        if current_game_state.player.state == "died":
            print(f"Level finished. Score of {0} was added to list.")
            self.play_scores.append({"score":0,"player_state":current_game_state.player.state})
            self.dump_scores_to_json(0, current_game_state.level_time)

        # Call the specific implementation of play
        fly = self._play_impl(current_game_state)
        
        # Visualize new play state
        self.visualize_positions(current_game_state)

        return fly
    


    @abstractmethod
    def _play_impl(self, current_game_state):
        pass

    @abstractmethod
    def get_name(self):
        pass
