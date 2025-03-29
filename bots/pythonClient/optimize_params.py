import time
import json
import optuna
from datetime import datetime

# Define the objective function for Optuna
def objective(trial):
    # Suggest values for the parameters
    boarder_factor = trial.suggest_float("boarder_factor", 0.0, 1.0)
    obstacle_factor = trial.suggest_float("obstacle_factor", 0.0, 2.0)
    coin_factor = trial.suggest_float("coin_factor", 0.0, 2.0)

    # Set the parameters in the system
    data = {"force_baorder_factor": boarder_factor,"force_obstacle_factor":obstacle_factor,"force_coin_factor":coin_factor}
    with open(f"force_params.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    # Wait for the system to stabilize (simulate processing time)
    time.sleep(50)  # Simulate a delay for the system to process changes

    # Read in new score 
    with open("./current_Score.json", "r") as json_file:
        data = json.load(json_file)
        play_scores = data.get("play_scores", 0.1)

    # Return the negative of the score (since Optuna minimizes by default)
    return play_scores

# Create an Optuna study
start_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
study = optuna.create_study(direction="maximize", storage="sqlite:///db.sqlite3", study_name=f"force_optimization_{start_time}")  # We want to maximize the score


# Start the optimization process
print("Start with optimizing...")
study.optimize(objective, n_trials=20)  # Run 50 trials

# Print the best parameters after optimization
print(f"Optimization completed. Best parameters: {study.best_params}")
print(f"Best score: {-study.best_value}")  # Negate the value to get the actual score

# Apply the best parameters to the system
data = {"force_baorder_factor": study.best_params["boarder_factor"],"force_obstacle_factor":study.best_params["obstacle_factor"],"force_coin_factor":study.best_params["coin_factor"]}
with open(f"force_params.json", "w") as json_file:
    json.dump(data, json_file, indent=4)



print(f"Optimization completed. Current parameters: {study.best_params}")
