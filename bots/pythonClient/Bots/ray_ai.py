from Bots.bot_ai import BotAI
from Bots.data import PlayState

import json
import math
import random

#####Optimized params:
#{
#    "BOARDER_OFFSET": 8.920536559170113,
#    "BORDER_COL_OK_DIST": 222.8330725805445,
#    "BORDER_VERY_NEAR_BIRD": 150.91129702290522,
#    "BORDER_SCORE_RUN": 74.5636320013345,
#    "DISTANCE_TO_REACT": 336.78878687530505
#}

LOWER_Y_LIMIT = 29
UPPER_Y_LIMIT = 480
BOARDER_OFFSET = 8.920536559170113
BORDER_COL_OK_DIST = 222.8330725805445
BORDER_VERY_NEAR_BIRD =  150.91129702290522
BORDER_SCORE_RUN = 74.5636320013345

DISTANCE_TO_REACT = 336.78878687530505

class Ray_AI(BotAI):
    fly = True

    border_score = 0
    border_dir = True

    def collision_incomming(self, current_game_state: PlayState):
        y_up = current_game_state.player.pos_y + (current_game_state.player.height*1.8)
        y_low = current_game_state.player.pos_y - (current_game_state.player.height*1.8)

        coll_incom = False
        nearest_x_collission = 1000

        for obst in current_game_state.obstacles:
            if obst.type == "Coin":
                pass
            elif obst.type == "Seagull":
                y_b_up = obst.origin_y + obst.height*1.1
                y_b_low = obst.origin_y - obst.height*1.1
                #print(y_up, y_low, y_b_up, y_b_low)

                if (y_up > y_b_up) and (y_b_up > y_low):
                    #print("COND1")
                    coll_incom = True
                    if nearest_x_collission > obst.origin_x:
                        nearest_x_collission = obst.origin_x
                if (y_up > y_b_low) and (y_b_low > y_low):
                    #print("COND1")
                    coll_incom = True
                    if nearest_x_collission > obst.origin_x:
                        nearest_x_collission = obst.origin_x
            elif obst.type == "Raven":
                y_b_up = obst.origin_y + obst.height*1.5
                y_b_low = obst.origin_y - obst.height*1.5
                #print(y_up, y_low, y_b_up, y_b_low)

                if y_up > y_b_up > y_low:
                    coll_incom = True
                    if nearest_x_collission > obst.origin_x:
                        nearest_x_collission = obst.origin_x
                if y_up > y_b_low > y_low:
                    coll_incom = True
                    if nearest_x_collission > obst.origin_x:
                        nearest_x_collission = obst.origin_x

        return coll_incom , nearest_x_collission

    def nearest_bird(self, current_game_state: PlayState):

        num_of_birds = 0
        nearest_bird = None

        for obst in current_game_state.obstacles:
            if obst.type == "Seagull" or obst.type == "Raven":
                num_of_birds = num_of_birds+1
                if nearest_bird == None:
                    nearest_bird = obst
                else:
                    dist_to_bird = math.sqrt( (obst.origin_x - current_game_state.player.pos_x)**2 + (obst.origin_y - current_game_state.player.pos_y)**2   )
                    dist_to_nearest_bird = math.sqrt( (nearest_bird.origin_x - current_game_state.player.pos_x)**2 + (nearest_bird.origin_y - current_game_state.player.pos_y)**2   )
                    if dist_to_bird < dist_to_nearest_bird:
                        nearest_bird = obst

        return nearest_bird, num_of_birds
    
    def nearest_coin(self, current_game_state: PlayState):

        nearest_coin = None

        for obst in current_game_state.obstacles:
            if obst.type == "Coin":
                if nearest_coin == None:
                    nearest_coin = obst
                else:
                    X_OFFSET = -10
                    dist_to_nearest_coin = math.sqrt( (obst.origin_x - current_game_state.player.pos_x+X_OFFSET)**2 + (obst.origin_y - current_game_state.player.pos_y)**2   )
                    dist_to_nearest_bird = math.sqrt( (nearest_coin.origin_x - current_game_state.player.pos_x+X_OFFSET)**2 + (nearest_coin.origin_y - current_game_state.player.pos_y)**2   )
                    if dist_to_nearest_bird > dist_to_nearest_coin:
                        nearest_coin = obst

        return nearest_coin
    
    def coin_dir(self, current_game_state: PlayState):
        nearest_coin = self.nearest_coin(current_game_state)
        if nearest_coin is not None:
            print("COIN")
            if nearest_coin.origin_y < current_game_state.player.pos_y:
                return True
            else:
                return False
        else:
            # random
            print("COIN_RANDOM")
            return self.random_dir(current_game_state)
        
    def random_dir(self, current_game_state: PlayState, strict = False):

        if current_game_state.player.rotation < 0:
            return random.choice([True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
        else:
            return random.choice([True, True, True, True, True,True, True,True, True, True, True, True, True,True, True, True, True, True, True,True, True,True, True, True, True, True, True,True, False])


    def check_for_boarder(self, current_game_state: PlayState):
        if current_game_state.player.pos_y < (LOWER_Y_LIMIT + BOARDER_OFFSET):
            return True, False
        elif current_game_state.player.pos_y > (UPPER_Y_LIMIT - BOARDER_OFFSET):
            return True, True
        else:
            return False, False


    def ray_dir(self, current_game_state: PlayState, nearest_x_collission):
        nearest_bird, num_of_birds = self.nearest_bird(current_game_state)
        if nearest_bird is not None:
            border, dir = self.check_for_boarder(current_game_state)
            if border:
                dist_to_nearest_bird = math.sqrt( (nearest_bird.origin_x - current_game_state.player.pos_x)**2 + (nearest_bird.origin_y - current_game_state.player.pos_y)**2   )
                coll_dist = abs(nearest_x_collission - current_game_state.player.pos_x)
                print(dist_to_nearest_bird, coll_dist)
                if not ((dist_to_nearest_bird < BORDER_VERY_NEAR_BIRD) and (coll_dist > BORDER_COL_OK_DIST)):
                    print("BOARDER")
                    self.border_score = BORDER_SCORE_RUN
                    self.border_dir = dir
                    return dir
                else:
                    print("SKIP BORDER")
                
            print("RAY")
            if nearest_bird.origin_y < current_game_state.player.pos_y:
                return False
            else:
                return True
        else:
            # random
            print("RAY RANDOM")
            return self.random_dir(current_game_state)
        
    def _play_impl(self, current_game_state: PlayState):
        
        global BOARDER_OFFSET, BOARDER_OFFSET, BORDER_COL_OK_DIST, BORDER_VERY_NEAR_BIRD, BORDER_SCORE_RUN
        try:
            with open("./ray_params.json", "r") as json_file:
                data = json.load(json_file)
                BOARDER_OFFSET = data.get("BOARDER_OFFSET", 30)
                BORDER_COL_OK_DIST = data.get("BORDER_COL_OK_DIST", 300)
                BORDER_VERY_NEAR_BIRD = data.get("BORDER_VERY_NEAR_BIRD", 150)
                BORDER_SCORE_RUN = data.get("BORDER_VERY_NEAR_BIRD", 50)
                DISTANCE_TO_REACT = data.get("BORDER_VERY_NEAR_BIRD", 300)
                

        except Exception as  e:
            print(f"Paramupdate: {e}")


        if self.border_score > 0:
            self.border_score = self.border_score - 1
            print("BORDER SCORE")
            return self.border_dir
        
        # check if we should go out of the way
        nearest_bird, num_of_birds = self.nearest_bird(current_game_state)
        if (nearest_bird is not None):
            dist_to_nearest_bird = math.sqrt( (nearest_bird.origin_x - current_game_state.player.pos_x)**2 + (nearest_bird.origin_y - current_game_state.player.pos_y)**2   )
            if dist_to_nearest_bird < (DISTANCE_TO_REACT):
                coll, nearest_x_collission = self.collision_incomming(current_game_state)
                if (coll):
                    print(f"SHIT we will colide... {nearest_x_collission}")
                    # random 
                    return self.ray_dir(current_game_state, nearest_x_collission)
                else:
                    print("RANDOM")
                    return self.random_dir(current_game_state, strict=True)

            else:
                # go to coin
                return self.coin_dir(current_game_state)

        # go to coin
        return self.coin_dir(current_game_state)


    def get_name(self):
        return self.name

    def __init__(self):
        # todo: give your bot a super duper cool name
        self.name = "RayAI"
