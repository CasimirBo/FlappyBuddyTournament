import time
import json
import optuna
import os
from datetime import datetime
import statistics

BF = 0.5
CF = 0.0
# Define the objective function for Optuna
def objective(trial):
    # Suggest values for the parameters
    #boarder_factor = trial.suggest_float("boarder_factor", 0.1, 1.0)
    boarder_factor = BF
    obstacle_factor = trial.suggest_float("obstacle_factor", 0.1, 2.0)
    position_factor_xy = trial.suggest_float("position_factor_xy", 0.0, 1.0)

    coin_factor = CF

    # Set the parameters in the system
    data = {"force_boarder_factor": boarder_factor,"force_obstacle_factor":obstacle_factor,"force_position_factor_xy":position_factor_xy}
    with open(f"force2_params.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    # Wait for the system to stabilize (simulate processing time)
    time.sleep(15)

    # Define file, where to store the results of this run
    time2 = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    v2_output_file = f"./opt_data/opt/scores_{time2}.json"
    with open("./opt_data/folder_info.json", "w") as json_file:
        # You might want to structure the data more than just appending to `scores`
        json.dump({"output_file": v2_output_file}, json_file, indent=4)
    
    # Wait till we have enought finished levels
    NUMBER_OF_RESULTS = 5
    while True:
        time.sleep(5) 

        # Check 
        if os.path.exists(v2_output_file):
            with open(v2_output_file, "r") as json_file:
                data_scores = json.load(json_file)
                v2_scores = data_scores.get("scores", [])
                v2_times = data_scores.get("times", [])

                if len(v2_times) >= NUMBER_OF_RESULTS:
                    print("We have enought datapoints...")
                    break

    # calculate combined_score
    score_mean = statistics.median(v2_scores)
    time_mean = statistics.median(v2_times)
    combined_score = 0.001*score_mean + time_mean

    return combined_score

# Create an Optuna study
start_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
study = optuna.create_study(direction="maximize", storage="sqlite:///db.sqlite3", study_name=f"force2_optimization_{start_time}")  # We want to maximize the score


# Start the optimization process
print("Start with optimizing...")
study.optimize(objective, n_trials=10)  # Run 50 trials

# Print the best parameters after optimization
print(f"Optimization completed. Best parameters: {study.best_params}")
print(f"Best score: {-study.best_value}")  # Negate the value to get the actual score

# Apply the best parameters to the system
data = {"force_boarder_factor": BF,"force_obstacle_factor":study.best_params["obstacle_factor"],"force_position_factor_xy":study.best_params["position_factor_xy"]}
with open(f"force_params.json", "w") as json_file:
    json.dump(data, json_file, indent=4)



print(f"Optimization completed. Current parameters: {study.best_params}")
