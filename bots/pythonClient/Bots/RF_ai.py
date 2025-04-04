import tensorflow as tf
import numpy as np
import time

from Bots.bot_ai import BotAI
from Bots.data import PlayState


# Define a simple policy network
class PolicyNetwork(tf.keras.Model):
    def __init__(self, state_size):
        super(PolicyNetwork, self).__init__()
        self.dense1 = tf.keras.layers.Dense(16, activation='relu', input_shape=(state_size,))
        self.logits = tf.keras.layers.Dense(1)  # Output logits for binary decision
    
    def call(self, inputs):
        x = self.dense1(inputs)
        return self.logits(x)
    
class PolicyNetwork2(tf.keras.Model):
    def __init__(self, state_size):
        super(PolicyNetwork2, self).__init__()
        # First hidden layer with 32 units
        self.hidden1 = tf.keras.layers.Dense(32, activation='relu', input_shape=(state_size,))
        # Second hidden layer with 16 units
        self.hidden2 = tf.keras.layers.Dense(16, activation='relu')
        # Output layer with 1 unit (logit for binary decision: flap or not)
        self.logits = tf.keras.layers.Dense(1)
    
    def call(self, inputs):
        x = self.hidden1(inputs)
        x = self.hidden2(x)
        return self.logits(x)
    

# RL Agent encapsulating the policy network and training step
class RLAgent:
    def __init__(self, state_size):
        self.state_size = state_size
        #self.policy = PolicyNetwork(state_size)
        self.policy = PolicyNetwork2(state_size)
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    
    def act(self, state):
        # Reshape state and ensure it is float32
        state = np.array(state).reshape(1, -1).astype(np.float32)
        logits = self.policy(state)
        # Convert logits to probability (between 0 and 1)
        prob = tf.sigmoid(logits)
        # Sample an action: True if probability > random threshold, else False
        action = np.random.rand() < prob.numpy()[0][0]
        return action
    
    def train_step(self, state, action, reward):
        # Prepare the state and action for training
        state = np.array(state).reshape(1, -1).astype(np.float32)
        action_val = np.array([[1 if action else 0]], dtype=np.float32)
        
        # Record the current weights before the update
        old_weights = [w.numpy() for w in self.policy.trainable_variables]
        
        with tf.GradientTape() as tape:
            logits = self.policy(state)
            prob = tf.sigmoid(logits)
            loss = tf.keras.losses.binary_crossentropy(action_val, prob)
            loss *= reward  # scale the loss by the received reward

        #print(self.policy.trainable_variables)
        gradients = tape.gradient(loss, self.policy.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.policy.trainable_variables))
        
        # Record the new weights after the update
        new_weights = [w.numpy() for w in self.policy.trainable_variables]
        
        # Compute the L2 norm of the difference for each weight tensor
        weight_changes = [np.linalg.norm(new - old) for new, old in zip(new_weights, old_weights)]
        
        return loss.numpy(), weight_changes
    
agent = RLAgent(state_size=5)

last_score: int = 0
game_state = [0,0,0,0,0]
reward_of_last_step : float = 0
reward_of_last_steps : float = 0
last_action = True
direct_score = 0
normal_running = True


class RF_AI(BotAI):
    fly = True

    def _play_impl(self, current_game_state: PlayState):
        global last_score, play_state, reward_of_last_step, last_action, reward_of_last_steps, normal_running, game_state, direct_score



        if normal_running:
            reward_of_last_step = current_game_state.score - last_score
            reward_of_last_steps = (9/10)*reward_of_last_steps + (1/10)*reward_of_last_step
        else:
            normal_running = True


        if current_game_state.player.state == "died":
            direct_score  = 50
            reward_of_last_steps = 0 -1
            normal_running = False
        elif current_game_state.player.state == "finished":
            direct_score = 0
            reward_of_last_steps = reward_of_last_steps + 1
            normal_running = False
        else:
            direct_score = 0.1

        if reward_of_last_step < 0:
            reward_of_last_step = 0
        play_state = current_game_state
        last_score = current_game_state.score

        #print(reward_of_last_step)

        coin = None
        bird = None
        for obst in current_game_state.obstacles:
            if obst.type == "Coin":
                if coin == None:
                    coin = obst
                if (abs(coin.origin_x - current_game_state.player.pos_x) + abs(coin.origin_y - current_game_state.player.pos_y)) > (abs(obst.origin_x - current_game_state.player.pos_x) + abs(obst.origin_y - current_game_state.player.pos_y)):
                    coin = obst
                
            if obst.type == "Seagull" or obst.type == "Raven":
                if bird == None:
                    bird = obst
                if (abs(bird.origin_x - current_game_state.player.pos_x) + abs(bird.origin_y - current_game_state.player.pos_y)) > (abs(obst.origin_x - current_game_state.player.pos_x) + abs(obst.origin_y - current_game_state.player.pos_y)):
                    bird = obst

        if coin == None and bird == None:
            game_state = [current_game_state.player.pos_y,-1000,          -1000         ,-1000,          -1000              ]
        elif coin == None:
            game_state = [current_game_state.player.pos_y, bird.origin_x, bird.origin_y , -1000,          -1000             ]
        elif bird == None:
            game_state = [current_game_state.player.pos_y, -1000,          -1000        ,coin.origin_x, coin.origin_y       ]
        else:
            game_state = [current_game_state.player.pos_y, bird.origin_x, bird.origin_y ,coin.origin_x, coin.origin_y       ]
        #print(f"game_state: {game_state} ")
        action = agent.act(game_state)

        #print(f"game_state: {game_state} | action: {action} type({type(action)})")
        last_action = action
        return bool(action)

    def get_name(self):
        return self.name

    def __init__(self):
        self.name = "RF_AI"
        self.token_id = None


# Dummy function to get a game state (e.g., a vector of observations)
def get_game_state():
    global game_state
    # Example: return a random state vector (state_size = 4)
    return game_state

# Dummy function to simulate getting a reward from the game
def get_reward():
    global last_score
    # Example: return a random reward
    return last_score




# Main game loop simulation
def training_loop():
    global last_score, game_state, reward_of_last_steps, last_action, direct_score, reward_of_last_step

    while True:
        
        rew = reward_of_last_step/100

        # Train the agent using the observed transition
        loss, weight_changes = agent.train_step(game_state, last_action, rew)
        # Optional: print loss for debugging
        print("Loss: ", loss, " game_state: " ,game_state," last_action: ", last_action, " Reward: ", rew, " weight_changes: ", weight_changes)

        time.sleep(0.01)
