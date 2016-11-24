#Pong! 

import math, random

#Game Constants
GRID_SIZE = 12
GAME_SIZE = 1.0
PADDLE_H = 0.2
PADDLE_X = 1.0
PADDLE_WIDTH = 0.01
MOVE_UP = 0.04
MOVE_STAY = 0.0
MOVE_DOWN = -0.04
MOVES = [MOVE_DOWN, MOVE_STAY, MOVE_UP]
Y_ZERO_THRESHOLD = 0.01

GAMMA = 0.8
ALPHA = 10.0
EPSILON = 10000

SIMULATIONS = 10000

#Q Representation
#GRID_SIZExGRID_SIZE grid ball locations, 2 x velocities, 3 y velocities, GRID_SIZE paddle positions, 3 paddle movements
q_vals = [[[[[[
	[0.0]*2 for i in range(3)] 
	for i in range(GRID_SIZE)]  
	for i in range(3)]  
	for i in range(2)] 
	for i in range(GRID_SIZE)] 
	for i in range(GRID_SIZE)]

#State Variables (start vals)
ball_x_start = GAME_SIZE / 2.0
ball_y_start = GAME_SIZE / 2.0
velocity_x_start = 0.03
velocity_y_start = 0.01
paddle_y_start = ball_y_start - PADDLE_H / 2 #top of paddle

# ------ Functions to convert state into Q space ------ #

#X/Y_ball convert
def get_loc_q(v):
	r = int(math.floor(v * GRID_SIZE))
	if r >= GRID_SIZE:
		return GRID_SIZE - 1
	else:
		return r

#X Velocity Ball convert
def get_xvel_q(x_vel):
	if x_vel >= 0:
		return 1
	else:
		return 0 #not actually 0, represents -1

#Y Velocity Ball convert
def get_yvel_q(y_vel):
	if abs(y_vel) > Y_ZERO_THRESHOLD:
		return get_xvel_q(y_vel) + 1
	else:
		return 0

#Paddle location convert
def get_paddle_q(y):
	return int(math.floor(GRID_SIZE * y) / (1.0 - PADDLE_H))

def get_q_val(x, y, vx, vy, py, m):
	#pri get_loc_q(x), get_loc_q(y), get_xvel_q(vx), get_yvel_q(vy), get_paddle_q(py), m

	return q_vals[get_loc_q(x)][get_loc_q(y)][get_loc_q(vx)][get_loc_q(vy)][get_loc_q(py)][m][0]

def set_q_val(x, y, vx, vy, py, m, v):
	q_vals[get_loc_q(x)][get_loc_q(y)][get_loc_q(vx)][get_loc_q(vy)][get_loc_q(py)][m][0] = v
	inc_q_visited(x, y, vx, vy, py, m)

def get_q_visited(x, y, vx, vy, py, m):
	return q_vals[get_loc_q(x)][get_loc_q(y)][get_loc_q(vx)][get_loc_q(vy)][get_loc_q(py)][m][1]

def inc_q_visited(x, y, vx, vy, py, m):
	val = q_vals[get_loc_q(x)][get_loc_q(y)][get_loc_q(vx)][get_loc_q(vy)][get_loc_q(py)][m][1]
	q_vals[get_loc_q(x)][get_loc_q(y)][get_loc_q(vx)][get_loc_q(vy)][get_loc_q(py)][m][1] = val + 1

# ----- Step action ----- #


#Helpers
def is_in_paddle(x, y, pad_y):
	if x >= PADDLE_X and y < pad_y + (PADDLE_H / 2) and y > pad_y - (PADDLE_H / 2):
		return True
	return False

def get_rand_x():
	return (random.random() * Y_ZERO_THRESHOLD * 2) - Y_ZERO_THRESHOLD
def get_rand_y():
	return (random.random() * Y_ZERO_THRESHOLD * 4) - Y_ZERO_THRESHOLD * 2

def get_ALPHA(ball_x, ball_y, vel_x, vel_y, pad_y, move):
	if ball_x < 0.0:
		ball_x = 0.0
	if ball_x >= 1.0:
		ball_x = 1.0
	if ball_y < 0.0:
		ball_y = 0.0
	if ball_y >= 1.0:
		ball_y = 1.0
	t = get_q_visited(ball_x, ball_y, vel_x, vel_y, pad_y + MOVES[move], move)
	return ALPHA / (ALPHA + t)

def is_unvisited_move(ball_x, ball_y, vel_x, vel_y, pad_y, move):
	if get_q_visited(ball_x, ball_y, vel_x, vel_y, pad_y, move) < EPSILON:
		return True
	return False

def choose_move(ball_x, ball_y, vel_x, vel_y, pad_y):
	actions = [0, 1, 2]
	qt = get_q_futures_threshold(ball_x, ball_y, vel_x, vel_y, pad_y)
	qs = get_q_futures(ball_x, ball_y, vel_x, vel_y, pad_y)
	maxQ = 0
	if len(qt) == 0:
		maxQ = max(qs)
	else:
		maxQ = max(qt)

	count = qs.count(maxQ)
	if count > 1:
		indices = [index for index, val in enumerate(qs) if val == maxQ]
		i = random.choice(indices)
	else:
		i = qs.index(maxQ)

	return i, MOVES[i]

def get_q_futures(ball_x, ball_y, vel_x, vel_y, pad_y):
	ball_x = ball_x + vel_x
	ball_y = ball_y + vel_y
	if ball_x < 0.0:
		ball_x = 0.0
	if ball_x >= 1.0:
		ball_x = 1.0
	if ball_y < 0.0:
		ball_y = 0.0
	if ball_y >= 1.0:
		ball_y = 1.0
	futures = []
	for i, v in enumerate(MOVES):
		futures.append(get_q_val(ball_x, ball_y, vel_x, vel_y, pad_y + MOVES[i], i))
	return futures

def get_q_futures_threshold(old_ball_x, old_ball_y, vel_x, vel_y, pad_y):
	ball_x = old_ball_x + vel_x
	ball_y = old_ball_y + vel_y
	if ball_x < 0.0:
		ball_x = 0.0
	if ball_x >= 1.0:
		ball_x = 1.0
	if ball_y < 0.0:
		ball_y = 0.0
	if ball_y >= 1.0:
		ball_y = 1.0
	futures = []
	for i, v in enumerate(MOVES):
		if is_unvisited_move(old_ball_x, old_ball_y, vel_x, vel_y, pad_y, i):
			futures.append(get_q_val(ball_x, ball_y, vel_x, vel_y, pad_y + MOVES[i], i))
	return futures



def update_q(ball_x, ball_y, vel_x, vel_y, pad_y, move, r, t): #should limit moves
	if (ball_x > GAME_SIZE):
		ball_x = GAME_SIZE
	if (ball_x < 0.0):
		ball_x = 0.0

	if (ball_y > GAME_SIZE):
		ball_y = GAME_SIZE
	if (ball_y < 0.0):
		ball_y = 0.0
	#for each move: move up, down, stay
	cur_q = get_q_val(ball_x, ball_y, vel_x, vel_y, pad_y, move)
	#look at future potential moves
	g = (GAMMA * max(get_q_futures(ball_x, ball_y, vel_x, vel_y, pad_y)))
	newval = (cur_q + (get_ALPHA(ball_x, ball_y, vel_x, vel_y, pad_y, move) * (r + g - cur_q) ) )
	set_q_val(ball_x, ball_y, vel_x, vel_y, pad_y, move, newval)
	return 

def update_all_q(ball_x, ball_y, vel_x, vel_y, pad_y, reward, t):
	update_q(ball_x, ball_y, vel_x, vel_y, pad_y, 0, reward, t)
	update_q(ball_x, ball_y, vel_x, vel_y, pad_y, 1, reward, t)
	update_q(ball_x, ball_y, vel_x, vel_y, pad_y, 2, reward, t)

#Main step
def step(ball_x, ball_y, vel_x, vel_y, pad_y, stepnum):
	#Increment ball_x by velocity_x and ball_y by velocity_y.
	ball_x += vel_x
	ball_y += vel_y

	#Bounce:
	if (ball_y < 0):
		ball_y = -ball_y
		vel_y = -vel_y
	if (ball_y > 1):
		ball_y = 2 - ball_y
		vel_y = -vel_y
	if (ball_x < 0):
		ball_x = -ball_x
		vel_x = -vel_x

	move, moveval = choose_move(ball_x, ball_y, vel_x, vel_y, pad_y)
	if (pad_y + moveval) + (PADDLE_H/2.0) > GAME_SIZE:
		moveval = GAME_SIZE - (PADDLE_H/2.0) - pad_y
	if (pad_y + moveval) - (PADDLE_H/2.0) < 0:
		moveval = (PADDLE_H/2.0) - pad_y
		
	if (is_in_paddle(ball_x, ball_y, pad_y)):
		update_q(ball_x, ball_y, vel_x, vel_y, pad_y, move, 1.0, stepnum)
		ball_x = 2 * PADDLE_X - ball_x
		vel_x = -vel_x + get_rand_x()
		vel_y = vel_y + get_rand_y()
		if (abs(vel_x) <= 0.03):
			if vel_x < 0:
				vel_x = -0.03
			else:
				vel_x = 0.03	
		return ball_x, ball_y, vel_x, vel_y, pad_y + moveval, 1, False
	elif (ball_x > PADDLE_X):
		update_q(ball_x, ball_y, vel_x, vel_y, pad_y, move, -1.0, stepnum)
		return ball_x, ball_y, vel_x, vel_y, pad_y + moveval, 0, True
	else:
		update_q(ball_x, ball_y, vel_x, vel_y, pad_y, move, 0.0, stepnum) ###Should update Q with current reward, doesn't happen because bounce occurs before this...

	#return updated values and info about termination
	return ball_x, ball_y, vel_x, vel_y, pad_y + moveval, 0, False



# ------ Main stuff ------ #

def run_simulations():
	max_rebounds = 0
	convergence_threshold = 10
	bounces_total = 0.0
	bounces_sims = 1.0
	sims_to_reach_threshold = -1
	for i in xrange(SIMULATIONS):
		ball_x = ball_x_start
		ball_y = ball_y_start
		vel_x = velocity_x_start
		vel_y = velocity_y_start
		pad_y =  paddle_y_start
		paddle_hits = 0
		hit_paddle = 0
		stepnum = 0		
		while(True):
			ball_x, ball_y, vel_x, vel_y, pad_y, hit_paddle, terminated = step(ball_x, ball_y, vel_x, vel_y, pad_y, stepnum)
			if terminated:
				break
			stepnum += 1
			paddle_hits += hit_paddle
		if paddle_hits > max_rebounds:
			max_rebounds = paddle_hits
			print paddle_hits
		if max_rebounds > convergence_threshold:
			bounces_total += paddle_hits
			bounces_sims += 1
			if sims_to_reach_threshold < 0:
				sims_to_reach_threshold = i
	print "--------------------------------------------"
	print "STATS: SIMULATIONS:", SIMULATIONS, "GAMMA", GAMMA, "EPSILON:", EPSILON, "ALPHA: ", ALPHA
	print "LARGEST REBOUND NUMBER ", max_rebounds
	print "AVERAGE BOUNCES POST CONVERGE  ", (bounces_total / bounces_sims)
	print "SIMULATIONS TO CONVERGE  ", sims_to_reach_threshold


if __name__ == '__main__':
	# if len(sys.argv) == 6:
	# 	SIMULATIONS = sys.argv[1]
	# 	GRID_SIZE = sys.argv[2]
	# 	GAMMA = sys.argv[3]
	# 	ALPHA = sys.argv[4]
	# 	EPSILON = sys.argv[5]
	run_simulations()


















