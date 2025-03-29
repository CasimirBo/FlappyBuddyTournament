
import pyqtgraph as pg
import numpy as np

from Bots.bot_ai import BotAI
from Bots.data import PlayState



class ForceAI(BotAI):
    fly = True

    ylimit = 768
    xlimit= 512

    _debug_viz_upper_force = None
    _debug_viz_lower_force = None
    _debug_viz_border_force = None
    _debug_viz_obstacle_force = None

    obstacles_force_inf_position_scatter = pg.ScatterPlotItem(pen=None, symbol='x', size=20, brush='#FF0000FF')
    BotAI.plot.addItem(obstacles_force_inf_position_scatter)
    BotAI.legend.addItem(obstacles_force_inf_position_scatter, "Obstacles with force influance")

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
        #print(upper_force, lower_force, border_force)
        
        #self._debug_viz_upper_force = self._update_line(self._debug_viz_upper_force, (0,0), upper_force) # upper force
        #self._debug_viz_lower_force = self._update_line(self._debug_viz_lower_force, (0,lower_ref), lower_force)  # lower force
        self._debug_viz_border_force = self._update_line(self._debug_viz_border_force, (0-20,lower_ref/2), border_force)     #boarder force

        return border_force	

    def _calc_obstacle_force(self, current_game_state: PlayState):

        obstacles_with_force_influance = [] # for debug

        obstacle_positions = []
        obstacle_forces = []
    
        for obstacle in current_game_state.obstacles:
            if obstacle.type == "Seagull" or obstacle.type == "Raven":
                x_diff = current_game_state.player.pos_x-obstacle.origin_x
                y_diff = current_game_state.player.pos_y-obstacle.origin_y
                if (x_diff) < 30: # we do not take anything into account, that we passed already
                    obstacles_with_force_influance.append({'pos': (obstacle.origin_x, obstacle.origin_y)}) # for debug
                    if x_diff == 0 and y_diff == 0:
                        obstacle_forces.append(np.array([0,0]))
                    elif x_diff == 0:
                        obstacle_forces.append(np.array([0,self.ylimit/y_diff]))
                    elif y_diff == 0:
                        obstacle_forces.append(np.array([self.xlimit/x_diff, 0]))
                    else:
                        obstacle_forces.append(np.array([self.xlimit/x_diff,self.ylimit/y_diff]))
                    obstacle_positions.append(np.array([(obstacle.origin_x),(obstacle.origin_y)]))

        self.obstacles_force_inf_position_scatter.setData(obstacles_with_force_influance)

        if obstacle_forces:  # Ensure the list is not empty
            obstacle_force = np.median(np.array(obstacle_forces), axis=0)
            obstacle_position = np.median(np.array(obstacle_positions), axis=0)
        else:
            obstacle_force = np.array([0, 0])  # Fallback if list is empty
            obstacle_position = np.array([0, 0])  # Fallback if list is empty

        self._debug_viz_obstacle_force = self._update_line(self._debug_viz_obstacle_force, (obstacle_position[0],obstacle_position[1]), obstacle_force)     #obstacle force

        return obstacle_force	

    
    def _suggest_fly(self, current_game_state: PlayState):
        
        # Calculate forces
        border_force = self._calc_border_force(current_game_state)
        obstacle_force = self._calc_obstacle_force(current_game_state)
        
        # Combine forces 
        baorder_factor = 2
        obstacle_factor = 1
        force = baorder_factor*border_force + obstacle_factor*obstacle_force

        decision = baorder_factor*border_force[1] + obstacle_factor*obstacle_force[1]*abs(obstacle_force[0])
        # Debug forces
        print(f"Decision {decision} | CombinedForce: {force} | Border: {border_force} | Obstacle: {obstacle_force}")



        

        # Derive fly from force
        if decision > 0:
            self.fly = False
        else:
            self.fly = True


    def _play_impl(self, current_game_state: PlayState):

        
        self._suggest_fly(current_game_state)

        
        return self.fly

    def get_name(self):
        return self.name

    def __init__(self):
        # todo: give your bot a super duper cool name
        self.name = "Force"


