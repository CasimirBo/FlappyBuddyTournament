
import pyqtgraph as pg
import numpy as np
import json
import copy
import math

from Bots.bot_ai import BotAI
from Bots.data import PlayState

# gloabl parameters to optimize
force_baorder_factor = 2
force_obstacle_factor = 1
force_coin_factor = 0.2




class Force2AI(BotAI):

    fly = True

    ylimit = 768
    xlimit= 512

    _debug_viz_border_force = None
    _debug_viz_obstacle_force = None
    _debug_viz_coin_force = None

    obstacles_force_inf_position_scatter = pg.ScatterPlotItem(pen=None, symbol='x', size=20, brush='#FF0000FF')
    BotAI.plot.addItem(obstacles_force_inf_position_scatter)
    BotAI.legend.addItem(obstacles_force_inf_position_scatter, "Obstacles with force influance")

    coins_force_inf_position_scatter = pg.ScatterPlotItem(pen=None, symbol='x', size=20, brush='#FFF347FF')
    BotAI.plot.addItem(coins_force_inf_position_scatter)
    BotAI.legend.addItem(coins_force_inf_position_scatter, "Coins with force influance")

    obstacles_art_obs_position_scatter = pg.ScatterPlotItem(pen=None, symbol='o', size=10, brush='#48F3FFFF')
    BotAI.plot.addItem(obstacles_art_obs_position_scatter)
    BotAI.legend.addItem(obstacles_art_obs_position_scatter, "Artificals")


    def _update_line(self, line_obj, start, direction):

        x0, y0 = start
        x_direction, y_direction = direction
        x1 = x0 + x_direction
        y1 = y0 + y_direction

        if line_obj is not None:
            line_obj.setData([x0, x1], [y0, y1])
            return line_obj
        else:
            # Otherwise, create a new line object.
            line_obj = BotAI.plot.plot([x0, x1], [y0, y1], pen=pg.mkPen(color="w", width=2))
            BotAI.legend.addItem(line_obj, "Nearest Coin")
        return line_obj

    def _calc_border_force(self, current_game_state: PlayState):
        
        # calculate forces 
        upper_ref = 0
        lower_ref = self.xlimit

        upper_force = np.array([0,(lower_ref/(current_game_state.player.pos_y - upper_ref))])
        lower_force = np.array([0,(lower_ref/(current_game_state.player.pos_y - lower_ref))])
       
        border_force = upper_force + lower_force

        # debugging
        self._debug_viz_border_force = self._update_line(self._debug_viz_border_force, (0-20,200), border_force)     #boarder force

        return border_force	

    def _calc_obstacle_force(self, current_game_state: PlayState, force_position_factor_xy):

        obstacles_with_force_influance = [] # for debug

        obstacle_positions = []
        obstacle_forces = []
    
        for obstacle in current_game_state.obstacles:
            if obstacle.type == "Seagull" or obstacle.type == "Raven":
                x_diff = current_game_state.player.pos_x-obstacle.origin_x
                y_diff = current_game_state.player.pos_y-obstacle.origin_y
                #print(x_diff)
                if (x_diff) < 90: # we do not take anything into account, that we passed already
                    obstacles_with_force_influance.append({'pos': (obstacle.origin_x, obstacle.origin_y)}) # for debug
                    if x_diff == 0 and y_diff == 0:
                        obstacle_forces.append(np.array([0,0]))
                    elif y_diff == 0:
                        obstacle_forces.append(np.array([0, 0]))
                    else:
                        obstacle_forces.append(np.array( [0,(self.ylimit/y_diff)]  ) )

                    obstacle_positions.append(np.array([(obstacle.origin_x),(obstacle.origin_y)]))

        self.obstacles_force_inf_position_scatter.setData(obstacles_with_force_influance)

        if obstacle_forces:  # Ensure the list is not empty
            # forces und positions gewichten basierend auf abstand:

            obstacle_positions_corrected = []

            for index, p in enumerate(obstacle_positions):
                x_diff = current_game_state.player.pos_x - p[0]
                y_diff = current_game_state.player.pos_y - p[1]
                
                # Calculate the inverse of the distance as the factor
                distance = abs(x_diff)*force_position_factor_xy + abs(y_diff)*(1-force_position_factor_xy)
                if distance != 0:
                    factor = self.xlimit / distance  # the closer the obstacle, the higher the factor
                else:
                    factor = self.xlimit  # if the player and obstacle are at the same position, no change
                
                # Scale the obstacle's position by the factor but maintain the original scale
                p_fac = (
                    p[0] * factor,  # Adjust the x-position based on the factor
                    p[1] * factor   # Adjust the y-position based on the factor
                )

                #print(factor)
                obstacle_forces[index][0] = obstacle_forces[index][0]*factor
                obstacle_forces[index][1] = obstacle_forces[index][1]*factor
                

                obstacle_positions_corrected.append(p_fac)

            obstacle_force = np.median(np.array(obstacle_forces), axis=0)

            obstacle_position = np.median(np.array(obstacle_positions_corrected), axis=0)
        else:
            obstacle_force = np.array([0, 0])  # Fallback if list is empty
            obstacle_position = np.array([0, 0])  # Fallback if list is empty

        self._debug_viz_obstacle_force = self._update_line(self._debug_viz_obstacle_force, (100,200), obstacle_force)     #obstacle force

        return obstacle_force	

    def _calc_coin_force(self, current_game_state: PlayState):

        coins_with_force_influance = [] # for debug

        coin_positions = []
        coin_forces = []
    
        for obstacle in current_game_state.obstacles:
            if obstacle.type == "Coin":
                x_diff = current_game_state.player.pos_x-obstacle.origin_x
                y_diff = current_game_state.player.pos_y-obstacle.origin_y

                if ((x_diff) < 50 ): # we do not take anything into account, that we passed already
                    if coin_positions == []:
                        coins_with_force_influance.append({'pos': (obstacle.origin_x, obstacle.origin_y)}) # for debug
                        if x_diff == 0 and y_diff == 0:
                            coin_forces.append(np.array([0,0]))
                        elif x_diff == 0:
                            coin_forces.append(np.array([0,self.ylimit/y_diff]))
                        elif y_diff == 0:
                            coin_forces.append(np.array([self.xlimit/x_diff, 0]))
                        else:
                            coin_forces.append( np.array([self.xlimit/x_diff,self.ylimit/y_diff]))
                        coin_positions.append(np.array([(obstacle.origin_x),(obstacle.origin_y)]))
                    elif (abs(x_diff)+abs(y_diff))  < (abs(current_game_state.player.pos_x-coin_positions[0][0])+abs(current_game_state.player.pos_y-coin_positions[0][1])) : # we add only hte nearest coin force 
                        coins_with_force_influance[0] = {'pos': (obstacle.origin_x, obstacle.origin_y)} # for debug
                        if x_diff == 0 and y_diff == 0:
                            coin_forces[0] = np.array([0,0])
                        elif x_diff == 0:
                            coin_forces[0] = np.array([0,self.ylimit/y_diff])
                        elif y_diff == 0:
                            coin_forces[0] = np.array([self.xlimit/x_diff, 0])
                        else:
                            coin_forces[0] = np.array([self.xlimit/x_diff,self.ylimit/y_diff])
                        coin_positions[0] = np.array([(obstacle.origin_x),(obstacle.origin_y)])

        self.coins_force_inf_position_scatter.setData(coins_with_force_influance)

        if coin_forces:  # Ensure the list is not empty
            coin_force = np.median(np.array(coin_forces), axis=0)
            coin_position = np.median(np.array(coin_positions), axis=0)
        else:
            coin_force = np.array([0, 0])  # Fallback if list is empty
            coin_position = np.array([0, 0])  # Fallback if list is empty

        self._debug_viz_coin_force = self._update_line(self._debug_viz_coin_force, (coin_position[0],coin_position[1]), coin_force)     #obstacle force

        return coin_force	


    def _add_artifica_obstacles(self, current_game_state: PlayState):
        
        artificials = []

        # add the arrow
        for obstacle in current_game_state.obstacles[:]:
            if obstacle.type == "Seagull" or obstacle.type == "Raven":
                
                # boarder artificals
                #print(obstacle.origin_y)
                if obstacle.origin_y > 410:

                    # frontal2
                    obstacle_f2 = copy.deepcopy(obstacle)
                    obstacle_f2.origin_y = 520
                    obstacle_f2.origin_x = obstacle_f2.origin_x - (obstacle_f2.width*1.5)
                    current_game_state.obstacles.append(obstacle_f2)
                    artificials.append({'pos': (obstacle_f2.origin_x, obstacle_f2.origin_y)}) # viz

                    # frontal4
                    obstacle_f4 = copy.deepcopy(obstacle)
                    obstacle_f4.origin_y = 550
                    obstacle_f4.origin_x = obstacle_f4.origin_x - (obstacle_f4.width*2.4)
                    current_game_state.obstacles.append(obstacle_f4)
                    artificials.append({'pos': (obstacle_f4.origin_x, obstacle_f4.origin_y)}) # viz
                    

                if obstacle.origin_y < 90:

                    # frontal2
                    obstacle_f2 = copy.deepcopy(obstacle)
                    obstacle_f2.origin_y = -35
                    obstacle_f2.origin_x = obstacle_f2.origin_x - (obstacle_f2.width*1.5)
                    current_game_state.obstacles.append(obstacle_f2)
                    artificials.append({'pos': (obstacle_f2.origin_x, obstacle_f2.origin_y)}) # viz

                    # frontal4
                    obstacle_f4 = copy.deepcopy(obstacle)
                    obstacle_f4.origin_y = -55
                    obstacle_f4.origin_x = obstacle_f4.origin_x - (obstacle_f4.width*2.4)
                    current_game_state.obstacles.append(obstacle_f4)
                    artificials.append({'pos': (obstacle_f4.origin_x, obstacle_f4.origin_y)}) # viz



                #print(f"({obstacle.origin_x}|{obstacle.origin_y})({obstacle_up.origin_x}|{obstacle_up.origin_y})")
                # viz
                


        self.obstacles_art_obs_position_scatter.setData(artificials)
                
        return current_game_state
    

    def _suggest_fly(self, current_game_state: PlayState, baorder_factor, obstacle_factor, coin_factor, force_position_factor_xy):
        
        # Add some artifical Obstacles
        current_game_state = self._add_artifica_obstacles(current_game_state)

        # Calculate forces
        border_force = self._calc_border_force(current_game_state)
        obstacle_force = self._calc_obstacle_force(current_game_state, force_position_factor_xy)
        coin_force = self._calc_coin_force(current_game_state)

        # Fuzzylogic for force combinations:

        obs = 0
        nearest_obstacle_dist = 100000
        for o in current_game_state.obstacles:
            if o.type == "Seagull" or o.type == "Raven":
                obs = obs + 1

                x_diff = abs(o.origin_x-current_game_state.player.pos_x)
                y_diff = abs(o.origin_y-current_game_state.player.pos_y)
                distance = math.sqrt(x_diff*x_diff + y_diff*y_diff)

                if distance < nearest_obstacle_dist:
                    nearest_obstacle_dist = distance

        #print(nearest_obstacle_dist)
        if obs == 0:
            #print(f"Number of obstacles: {obs} and nearest obstcale: {nearest_obstacle_dist} -> We follow the coin...")
            decision = - coin_force[1]
        else:
            if nearest_obstacle_dist > 500:
                #print(f"Number of obstacles: {obs} and nearest obstcale: {nearest_obstacle_dist}  -> Follow the coins...")
                decision = - coin_force[1]
            else:
                #print(f"Number of obstacles: {obs} and nearest obstcale: {nearest_obstacle_dist}  -> No coins anymore for us. It is to dangerous...")
                decision = (baorder_factor*border_force[1]) + (obstacle_factor*obstacle_force[1])

        
        
        # Debug forces

        # Derive fly from force
        if decision > 0:
            self.fly = False
        else:
            self.fly = True


    def _play_impl(self, current_game_state: PlayState):
        
        try:
            with open("./force2_params.json", "r") as json_file:
                data = json.load(json_file)
                force_baorder_factor = data.get("force_boarder_factor", 0.0)
                force_obstacle_factor = data.get("force_obstacle_factor", 0.0)
                force_coin_factor = data.get("force_coin_factor", 0.0)

                force_position_factor_xy = data.get("force_position_factor_xy", 1)
                

            self._suggest_fly(current_game_state, force_baorder_factor, force_obstacle_factor, force_coin_factor, force_position_factor_xy)
        except Exception as  e:
            print(f"Skipping fly suggestion: {e}")

        return self.fly

    def get_name(self):
        return self.name

    def __init__(self):
        # todo: give your bot a super duper cool name
        self.name = "Force2"


