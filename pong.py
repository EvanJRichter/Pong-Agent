#Pong! 

import math, random

#Game Constants
GRID_SIZE = 12, GAME_SIZE = 1.0
PADDLE_H = 0.2, PADDLE_X = 1.0, PADDLE_WIDTH = 0.01
MOVE_UP = 0.04, MOVE_STAY = 0.0, MOVE_DOWN = -0.04
MOVES = [MOVE_DOWN, MOVE_STAY, MOVE_UP]
Y_ZERO_THRESHOLD = 0.015

GAMMA = 0.8
ALPHA = 1.0
EPSILON = 0.05

SIMULATIONS = 1000.0
STEPS = 1000.0

#Q Representation
#12x12 grid ball locations, 2 x velocities, 3 y velocities, 12 paddle positions, 3 paddle movements
q_vals = [[[[[[[0] * GRID_SIZE] * 3] * 2] * GRID_SIZE] * 12] * 3] 

#State Variables (start vals)
ball_x_start = GAME_SIZE / 2.0
ball_y_start = GAME_SIZE / 2.0
velocity_x_start = 0.03
velocity_y_start = 0.01
paddle_y_start = ball_y_start - PADDLE_H / 2 #top of paddle

# ------ Functions to convert state into Q space ------ #

#X/Y_ball convert
def get_loc_q(v):
	return math.floor(v * GRID_SIZE)

#X Velocity Ball convert
def get_xvel_q(x_vel):
	if x_vel >= 0:
		return 1
	else
		return -1

#Y Velocity Ball convert
def get_yvel_q(y_vel):
	if math.abs(y_vel) > Y_ZERO_THRESHOLD:
		return get_xvel_q(y_vel)
	else
		return 0

#Paddle location convert
def get_paddle_q(y):
	return math.floor(GRID_SIZE * y) / (1.0 - PADDLE_H)

def get_q_val(x, y, vx, vy, py, m):
	return q_vals[get_loc_q(x)][get_loc_q(y)][get_loc_q(vx)][get_loc_q(vy)][get_loc_q(py)][m]

def set_q_val(x, y, vx, vy, py, m, v):
	q_vals[get_loc_q(x)][get_loc_q(y)][get_loc_q(vx)][get_loc_q(vy)][get_loc_q(py)][m] = v

# ----- Step action ----- #


#Helpers
def is_in_paddle(x, y, pad_y):
	if x >= PADDLE_X - PADDLE_WIDTH and y < pad_y + (PADDLE_H / 2) and y > pad_y - (PADDLE_H / 2):
		return True
	return False

def get_rand_x():
	return (random.random() * Y_ZERO_THRESHOLD * 2) - Y_ZERO_THRESHOLD
def get_rand_y():
	return (random.random() * Y_ZERO_THRESHOLD * 4) - Y_ZERO_THRESHOLD * 2

def get_reward(ball_x, ball_y, vel_x, vel_y, pad_y):
	if is_in_paddle(ball_x, ball_y, pad_y):
		return 1
	if ball_x > PADDLE_X:
		return -1
	return 0

def get_ALPHA(t):
	return STEPS / (STEPS - 1.0 + t)

def choose_move(ball_x, ball_y, vel_x, vel_y, pad_y):
	actions = [0, 1, 2]
	if random.random() < EPSILON: #exploration factor
        i = random.choice(actions)
    else:
        qs = get_q_futures(ball_x, ball_y, vel_x, vel_y, pad_y)
        maxQ = max(qs)
        count = q.count(maxQ)
        if count > 1:
            indices = [index for index, val in enumerate(qs) if val == maxQ]
            i = random.choice(indices)
        else:
            i = qs.index(maxQ)

	return i, MOVES[i]

def get_q_futures(ball_x, ball_y, vel_x, vel_y, pad_y):
	futures = []
	for i, v in enumerate(MOVES):
		futures.append(get_q_val(ball_x, ball_y, vel_x, vel_y, pad_y, i))
	return futures

def update_q(ball_x, ball_y, vel_x, vel_y, pad_y, t): #should limit moves
	#for each move: move up, down, stay
	for i, v in enumerate(MOVES):
		cur_q = get_q_val(ball_x, ball_y, vel_x, vel_y, pad_y, i)
		#look at future potential moves
		r = get_reward(ball_x, ball_y, vel_x, vel_y, pad_y)
		g = (GAMMA * max(get_q_futures(ball_x, ball_y, vel_x, vel_y, pad_y))
		newval = cur_q + (get_ALPHA(t) * (r + g - cur_q))
		set_q_val(ball_x, ball_y, vel_x, vel_y, pad_y, i, newval)
	return 


#Main step
def step(ball_x, ball_y, vel_x, vel_y, pad_y, stepnum):
	terminated = False
	hit_paddle = 0
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
	if (is_in_paddle(ball_x, ball_y, pad_y)):
		hit_paddle += 1
		ball_x = 2 * PADDLE_X - ball_x
		vel_x = -vel_x + get_rand_x()
		vel_y = vel_y + get_rand_y()
		if (math.abs(vel_x) <= 0.03):
			if vel_x < 0:
				vel_x = -0.03
			else:
				vel_x = 0.03	

	move, moveval = choose_move(ball_x, ball_y, vel_x, vel_y, pad_y)

	#update q of current spot based on future potential rewards
	update_q(ball_x, ball_y, vel_x, vel_y, pad_y, move, stepnum)

	if (ball_x > PADDLE_X):
		#terminate!
		return ball_x, ball_y, vel_x, vel_y, pad_y, hit_paddle, True

	#return updated values and info about termination
	return ball_x, ball_y, vel_x, vel_y, pad_y + moveval, hit_paddle, False



# ------ Main stuff ------ #

def run_simulations():
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
		print paddle_hits


if __name__ == '__main__':
	run_simulations()


















