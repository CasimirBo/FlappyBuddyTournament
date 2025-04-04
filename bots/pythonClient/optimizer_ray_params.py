import time
import json
import optuna
from datetime import datetime
import statistics
import os


# Define the objective function for Optuna
def objective(trial):
    # Suggest values for the parameters

    DISTANCE_TO_REACT = trial.suggest_float("DISTANCE_TO_REACT", 100, 500)
    BOARDER_OFFSET = trial.suggest_float("BOARDER_OFFSET", 5, 50)
    BORDER_COL_OK_DIST = trial.suggest_float("BORDER_COL_OK_DIST", 200, 500)
    BORDER_VERY_NEAR_BIRD = trial.suggest_float("BORDER_VERY_NEAR_BIRD", 50, 200)
    BORDER_SCORE_RUN = trial.suggest_float("BORDER_SCORE_RUN", 20, 100)
    DISTANCE_TO_REACT = trial.suggest_float("DISTANCE_TO_REACT", 100, 500)


    # Set the parameters in the system
    data = {
    "BOARDER_OFFSET": BOARDER_OFFSET,
    "BORDER_COL_OK_DIST": BORDER_COL_OK_DIST,
    "BORDER_VERY_NEAR_BIRD": BORDER_VERY_NEAR_BIRD,
    "BORDER_SCORE_RUN": BORDER_SCORE_RUN,
    "DISTANCE_TO_REACT": DISTANCE_TO_REACT
    }
    with open(f"ray_params.json", "w") as json_file:
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
    NUMBER_OF_RESULTS = 20
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
study = optuna.create_study(direction="maximize", storage="sqlite:///db.sqlite3", study_name=f"ray_optimization_{start_time}")  # We want to maximize the score


# Start the optimization process
print("Start with optimizing...")
study.optimize(objective, n_trials=100)  # Run 50 trials

# Print the best parameters after optimization
print(f"Optimization completed. Best parameters: {study.best_params}")
print(f"Best score: {-study.best_value}")  # Negate the value to get the actual score

# Apply the best parameters to the system
#data = {"force_baorder_factor": study.best_params["boarder_factor"],"force_obstacle_factor":study.best_params["obstacle_factor"],"force_coin_factor":study.best_params["coin_factor"]}
data = {
    "BOARDER_OFFSET": study.best_params["BOARDER_OFFSET"],
    "BORDER_COL_OK_DIST": study.best_params["BORDER_COL_OK_DIST"],
    "BORDER_VERY_NEAR_BIRD": study.best_params["BORDER_VERY_NEAR_BIRD"],
    "BORDER_SCORE_RUN": study.best_params["BORDER_SCORE_RUN"],
    "DISTANCE_TO_REACT": study.best_params["DISTANCE_TO_REACT"]
    }
with open(f"ray_params.json", "w") as json_file:
    json.dump(data, json_file, indent=4)



print(f"Optimization completed. Current parameters: {study.best_params}")
