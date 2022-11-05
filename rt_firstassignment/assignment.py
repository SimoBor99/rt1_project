from __future__ import print_function

import time
from sr.robot import *

a_th = 2.0
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

R = Robot()

def drive(speed, seconds):
	"""
	Function for setting a linear velocity
    
	Args: speed (int): the speed of the wheels
	seconds (int): the time interval
	"""
	R.motors[0].m0.power = speed
	R.motors[0].m1.power = speed
	time.sleep(seconds)
	R.motors[0].m0.power = 0
	R.motors[0].m1.power = 0
	
def turn(speed, seconds):
	"""
	Function for setting an angular velocity
    
	Args: speed (int): the speed of the wheels
	seconds (int): the time interval
	"""
	R.motors[0].m0.power = speed
	R.motors[0].m1.power = -speed
	time.sleep(seconds)
	R.motors[0].m0.power = 0
	R.motors[0].m1.power = 0

def find_token_silver():
	"""
	Function for finding the closest silver token
	
	Returns:
		dist_silver (float): distance of silver token (-1 if no silver token is detected)
		rot_y_silver (float): angle between the robot and silver token (-1 if no silver token is detected)
		silver_number ( int): the number of silver token ( -1 if no silver token is detected)
	"""
	dist_silver=100
	silver_token=False # this variable is false if the robot doesn't find the silver token, otherwise it's true
	for token in R.see():
		if token.info.marker_type is MARKER_TOKEN_SILVER and token.dist<dist_silver:
			dist_silver=token.dist
			rot_y_silver=token.rot_y
			silver_number=token.info.code
			silver_token=True
			
	if dist_silver==100 or not silver_token:
		return -1, -1, -1
	else:
		return dist_silver, rot_y_silver, silver_number

def find_token_gold():
	"""
	Function for finding the first gold token
	
	Returns:
		dist_gold (float): distance of the first gold token (-1 if no gold token is detected)
		rot_y_gold (float): angle between the robot and gold token (-1 if no gold token is detected)
		gold_number ( int): the number of gold token ( -1 if no gold token is detected)
	"""
	gold_token=False # this variable is false if the robot doesn't find the gold token, otherwise it's true
	for token in R.see():
		if token.info.marker_type is MARKER_TOKEN_GOLD:
			dist_gold=token.dist
			rot_y_gold=token.rot_y
			gold_number=token.info.code
			gold_token=True
	if not gold_token:
		return -1, -1, -1
	return dist_gold, rot_y_gold, gold_number
		
def align_to_silver( dist_silver, rot_y_silver):
	"""
	Function for aligning robot to the silver token
	
	Args: dist_silver (float): the distance of silver token
	rot_y_silver (float):  angle between the robot and the silver token

	Returns:
		silver_grab (boolean): if the silver token is grabbed (True) or not (False)
	"""
	silver_grab=False # this variable is false if the robot doesn't grab the silver token, otherwise it's true
	if dist_silver==-1:
		turn(5,1)
	elif dist_silver<d_th: 
		print("Found the silver!")
		if R.grab():# if we are close to the silver token, we grab it.
			print("Gotcha!")
			silver_grab=True
	elif -a_th<=rot_y_silver<= a_th: # if the robot is well aligned with the silver token, we go forward
		print("Ah, here we are!.")
		drive(30, 0.5)
	elif rot_y_silver<-a_th: # if the robot is not well aligned with the silver token, we move it on the left or on the right
		print("Left a bit for the silver...")
		turn(-3, 0.2)
	elif rot_y_silver>a_th:
		print("Right a bit for the silver...")
		turn(+3, 0.2)
	return silver_grab
	
def align_to_gold( dist_gold, rot_y_gold):
	"""
	Function for aligning robot to the gold token
	
	Args: dist_silver (float): the distance of gold token
	rot_y_silver (float):  angle between the robot and the gold token
	
	Returns:
		gold_reach (boolean): if the gold token is released (True) or not (False)
	"""
	gold_reach=False # this variable is false if the robot doesn't release the gold token, otherwise it's true
	if dist_gold==-1:
		turn(5,1)
	elif dist_gold< 1.6*d_th: 
		print("Found the gold!")
		if R.release():# if we are close to the gold token, we release it.
			print("Release!")
			gold_reach=True
	elif -a_th<=rot_y_gold<= a_th: # if the robot is well aligned with the gold token, we go forward
		print("Ah, here we are!.")
		drive(30, 0.5)
	elif rot_y_gold<-a_th: # if the robot is not well aligned with the gold token, we move it on the left or on the right
		print("Left a bit for the gold...")
		turn(-3, 0.2)
	elif rot_y_gold>a_th:
		print("Right a bit for the gold...")
		turn(+3, 0.2)
	return gold_reach
	
def check_paired_silver( parray_silver, silver_number):
	"""
	Function for checking if a silver token is paired
	
	Args: parray_silver (array of integer): it collects the code number of paired silver tokens
	number_silver (int): the code number of current silver token 
	
	Returns:
		paired (boolean): if the current silver token is paired (True) or not (False)
	"""
	paired=False
	j=0
	while j<6:
		if parray_silver[j]==silver_number: # if the current silver token has been already paired, the robot turns for finding a silver unpaired
			print("Token paired silver found")
			turn(10,2)
			paired=True
			break
		j+=1
	return paired

def check_paired_gold( parray_gold, gold_number):
	"""
	Function for checking if a gold token is paired
	
	Args: parray_gold (array of integer): it collects the code number of paired gold tokens
	number_gold (int): the code number of current gold token
	
	
	Returns:
		paired (boolean): if the current gold token is paired (True) or not (False)
	"""
	paired=False
	j=0
	while j<6:
		if parray_gold[j]==gold_number: # if the current gold token has been already paired, the robot turns for finding a gold unpaired
			print("Token paired gold found:")
			turn(10,2)
			paired=True
			break
		j+=1
	return paired
	
def paired_tokens( parray_silver, silver_number, parray_gold, gold_number, count_pair):
	"""
	Function for pairing tokens with their code number. In addition it checks if the robots has paired every silver token
	
	Args: parray_silver (array of integer): it collects the code number of paired silver tokens
	silver_number (int): the code number of current silver token
	parray_gold (array of integer): it collects the code number of paired gold tokens
	gold_number (int): the code number of current gold token
	count_pair (int): the number of paired tokens
	
	Returns:
		count_pair (int): the number of paired tokens, after the increment
	"""
	parray_silver[count_pair]=silver_number
	parray_gold[count_pair]=gold_number
	count_pair+=1
	if count_pair==6: # if every silver token has been paired, the program ends
		print("Finish, every silver token is paired")
		drive(-20,1)
		exit()
	else: # the robot moves and turns for finding the next silver token
		drive(-20,1)
		turn(25,2)
		print("Search the next silver token")
	return count_pair
	
def main():
	parray_silver=[0]*6 # this array collects the code number of paired silver tokens
	parray_gold=[0]*6 # this array collects the code number of paired gold tokens
	count_pair=0 # index for the access of previous arrays, and count the paired tokens
	silver_avaible=True # it is true if any silver token is avaible, otherwise it is false
	silver_taken=False # it is true if the silver token is grabbed, otherwise it is false
	gold_reach=False # it is true if the gold token is reached, otherwise it is false
	while 1:
		if silver_avaible:
			dist_silver, rot_y_silver, silver_number=find_token_silver()
			print("dist:", dist_silver,"rot:", rot_y_silver, "token: ", silver_number)
			paired_silver=check_paired_silver( parray_silver, silver_number)
			if not paired_silver and find_token_silver()!=-1: # if the robots finds an unpaired silver token, we can align to it
				silver_taken=align_to_silver( dist_silver, rot_y_silver)
			elif find_token_silver()==-1: # if no silver token is found, the robot turns
				turn(7,1)
		if silver_taken:
			silver_avaible=False
			dist_gold, rot_y_gold, gold_number=find_token_gold()
			print("dist:", dist_gold,"rot:", rot_y_gold, "token: ", gold_number)
			paired_gold=check_paired_gold( parray_gold, gold_number)
			if not paired_gold and find_token_gold()!=-1: # if the robots finds an unpaired gold token, we can align to it
				gold_reach=align_to_gold( dist_gold, rot_y_gold)
			elif find_token_silver()==-1: # if no gold token is found, the robot turns
				turn(7,1)
			if gold_reach:
				count_pair=paired_tokens( parray_silver, silver_number, parray_gold, gold_number, count_pair)
				silver_avaible=True
				silver_taken=False
				gold_reach=False
				
				
main()

		
	
			
		
