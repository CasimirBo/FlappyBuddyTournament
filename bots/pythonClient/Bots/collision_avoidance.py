from Bots.bot_ai import BotAI
from Bots.data import PlayState


class ColAvoidAI(BotAI):
    fly = True

    def _play_impl(self, current_game_state: PlayState):

        print(f"Player Position: ({current_game_state.player.pos_x}|{current_game_state.player.pos_y})")
        
        nearest_coin = None

        nearest_obstacle = None
        for obstacle in current_game_state.obstacles:
            if obstacle.type != "Coin":
                if nearest_obstacle is None:
                    nearest_obstacle = obstacle
                #elif (nearest_obstacle.origin_x-current_game_state.player.pos_x) > (obstacle.origin_x-current_game_state.player.pos_x):
                else:
                    dist_nearest = pow(nearest_obstacle.origin_x-current_game_state.player.pos_x,2) + pow(nearest_obstacle.origin_y-current_game_state.player.pos_y,2)
                    dist_obst = pow(obstacle.origin_x-current_game_state.player.pos_x,2) + pow(obstacle.origin_y-current_game_state.player.pos_y,2)
                    if dist_nearest > dist_obst:
                        nearest_obstacle = obstacle
            else:
                if nearest_coin is None:
                    nearest_coin = obstacle
                #elif nearest_coin.origin_x-current_game_state.player.pos_x > obstacle.origin_x-current_game_state.player.pos_x:
                else:
                    dist_nearest = pow(nearest_coin.origin_x-current_game_state.player.pos_x,2) + pow(nearest_coin.origin_y-current_game_state.player.pos_y,2)
                    dist_obst = pow(obstacle.origin_x-current_game_state.player.pos_x,2) + pow(obstacle.origin_y-current_game_state.player.pos_y,2)
                    if dist_nearest > dist_obst:
                        nearest_coin = obstacle
        

        if current_game_state.player.pos_y > 300: # got to y 300
            self.fly = True
        else:
            self.fly = False

        if nearest_coin is not None: # better go to nearest coin
            if nearest_coin.origin_y < current_game_state.player.pos_y:
                self.fly = True
            else:
                self.fly = False

        if nearest_obstacle is not None: # even better avaoid obstacle if there is one
            print(f"Nearest Obstacle {nearest_obstacle.type}: ({nearest_obstacle.origin_x}|{nearest_obstacle.origin_y}) ({nearest_obstacle.height})")

            if (nearest_obstacle.origin_x - current_game_state.player.pos_x) < 350: # only avoid if it is close
                print(abs(nearest_obstacle.origin_y - current_game_state.player.pos_y))
                if abs(nearest_obstacle.origin_y - current_game_state.player.pos_y) < (nearest_obstacle.height + current_game_state.player.height)*4: # only avoid if it is close
                    if nearest_obstacle.origin_y < current_game_state.player.pos_y:
                        self.fly = False
                    else:
                        self.fly = True

                nearest_obstacle.width

        return self.fly

    def get_name(self):
        return self.name

    def __init__(self):
        # todo: give your bot a super duper cool name
        self.name = "CollisionAvoidance"
