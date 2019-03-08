#this assignment was done as part of the Udacity AI for Robotics course. The move and sense functions were implemented by myself.

#this is localization in 2-d world. This is implemented using simple move and sense functions.
#uncertainty increases when moving but decreases when our agent senses a measurement. Our final state is thus determined
#by a series of move and sense functions.


# colors:
#    2D list, each entry either 'R' (for red cell) or 'G' (for green cell)

# measurements:
#    list of measurements taken by the robot, each entry either 'R' or 'G'
#
# motions:
#        list of actions taken by the robot, each entry of the form [dy,dx],
#        where dx refers to the change in the x-direction (positive meaning
#        movement to the right) and dy refers to the change in the y-direction
#        (positive meaning movement downward)
#        NOTE: the *first* coordinate is change in y; the *second* coordinate is
#              change in x

# sensor_right:
#        float between 0 and 1, giving the probability that any given
#        measurement is correct; the probability that the measurement is
#        incorrect is 1-sensor_right

# p_move:
#        float between 0 and 1, giving the probability that any given movement
#        command takes place; the probability that the movement command fails
#        (and the robot remains still) is 1-p_move; the robot will NOT overshoot
#        its destination in this exercise


# 1) first makes a movement,
# 2) then takes a measurement.
#
# Motion:
#  [0,0] - stay
#  [0,1] - right
#  [0,-1] - left
#  [1,0] - down
#  [-1,0] - up

pHit=0.6

pMiss=0.2

                                       

def move(p,p_move,motion):
 
 
   # w=len(colors)
   # h=len(colors[0])
   # p=[[1./(len(colors)*len(colors[0])) for x in range(w)] for y in range(h)] 

    
    aux=[[0.0 for row in range(len(p[0]))] for col in range(len(p))]
    
    
    for k in range(len(p)):
            for l in range(len(p[k])):
                aux[k][l]=p[(k-motion[0])%len(p)][(l-motion[1])%len(p[k])]*p_move+((1-p_move)*p[k][l])
        
    return aux
                
    
    #initialise p to be all equal
    #iterate through all elements
    #use total probability
    #use colors array
    
def sense(p,measurement,colors,sensor_right):
    
    #increase total belief
    #check for both right and wrong sensing
    #use pHit and pMiss values accordingly
    
    for k in range(len(p)):
            for l in range(len(p[0])):
                hit=(measurement==colors[k][l])
                p[k][l]=p[k][l]*(hit*sensor_right+(1-hit)*(1-sensor_right))
    return p            
            
            
    
    
def localize(colors,measurements,motions,sensor_right,p_move):
    # initializes p to a uniform distribution over a grid of the same dimensions as colors
 w=len(colors)
 h=len(colors[0])
    
 p=[[1./(len(colors)*len(colors[0])) for x in range(h)] for y in range(w)] 
    
    
    
    
    
 for i in range(len(motions)):
       # motion=motions[i]
        #measurement=measurements[i]
        p=move(p,p_move,motions[i])
       
        p=sense(p,measurements[i],colors,sensor_right)
    
 

 s=0

 for i in range(w):
    for j in range(h):
        s+=p[i][j]

 for i in range(w):
    for j in range(h):
        p[i][j]/=s

 return p
def show(p):
    rows = ['[' + ','.join(map(lambda x: '{0:.5f}'.format(x),r)) + ']' for r in p]
    print '[' + ',\n '.join(rows) + ']'
    
#sample test case is shown below.

colors = [['R','G','G','R','R'],
          ['R','R','G','R','R'],
          ['R','R','G','G','R'],
          ['R','R','R','R','R']]
measurements = ['G','G','G','G','G']
motions = [[0,0],[0,1],[1,0],[1,0],[0,1]]
p = localize(colors,measurements,motions,sensor_right = 0.7, p_move = 0.8)
show(p) # displays the final posterior distribution.
