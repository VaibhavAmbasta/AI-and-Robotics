#this is the particle filter implementation. The robot can now move in a circular motion. bearings to 4 landmark positions
#are our measurement criteria. Noise in sensors, motion step, bearing noise have also been considered.


from math import *
import random

# --------
# 
# some top level parameters
#

max_steering_angle = pi / 4.0 
bearing_noise = 0.1 
steering_noise = 0.1 
distance_noise = 5.0 

tolerance_xy = 15.0 # Tolerance for localization in the x and y directions.
tolerance_orientation = 0.25 # Tolerance for orientation.



# the "world" has 4 landmarks.
# the robot's initial coordinates are somewhere in the square
# represented by the landmarks.
#
# NOTE: Landmark coordinates are given in (y, x) form and NOT
# in the traditional (x, y) format!

landmarks  = [[0.0, 100.0], [0.0, 0.0], [100.0, 0.0], [100.0, 100.0]] # position of 4 landmarks in (y, x) format.
world_size = 100.0 # world is NOT cyclic. Robot is allowed to travel "out of bounds"

# ------------------------------------------------
# 
# this is the robot class
#

class robot:

    # --------
    # init: 
    #    creates robot and initializes location/orientation 
    #

    def __init__(self, length = 20.0):
        self.x = random.random() * world_size # initial x position
        self.y = random.random() * world_size # initial y position
        self.orientation = random.random() * 2.0 * pi # initial orientation
        self.length = length # length of robot
        self.bearing_noise  = 0.0 # initialize bearing noise to zero
        self.steering_noise = 0.0 # initialize steering noise to zero
        self.distance_noise = 0.0 # initialize distance noise to zero

    # --------
    # set: 
    #    sets a robot coordinate
    #

    def set(self, new_x, new_y, new_orientation):

        if new_orientation < 0 or new_orientation >= 2 * pi:
            raise ValueError, 'Orientation must be in [0..2pi]'
        self.x = float(new_x)
        self.y = float(new_y)
        self.orientation = float(new_orientation)

    # --------
    # set_noise: 
    #    sets the noise parameters
    #
    def set_noise(self, new_b_noise, new_s_noise, new_d_noise):
        # makes it possible to change the noise parameters
        # this is often useful in particle filters
        self.bearing_noise  = float(new_b_noise)
        self.steering_noise = float(new_s_noise)
        self.distance_noise = float(new_d_noise)

    # --------
    # measurement_prob
    #    computes the probability of a measurement
    #  

    def measurement_prob(self, measurements):

        # calculate the correct measurement
        # sequentially considers all 4 bearing measurements
        predicted_measurements = self.sense(0) # Our sense function took 0 as an argument to switch off noise.


        # compute errors
        error = 1.0
        for i in range(len(measurements)):
            error_bearing = abs(measurements[i] - predicted_measurements[i])
            error_bearing = (error_bearing + pi) % (2.0 * pi) - pi # truncate
            

            # update Gaussian
            error *= (exp(- (error_bearing ** 2) / (self.bearing_noise ** 2) / 2.0) /  
                      sqrt(2.0 * pi * (self.bearing_noise ** 2)))

        return error
    
    def __repr__(self): #allows us to print robot attributes.
        return '[x=%.6s y=%.6s orient=%.6s]' % (str(self.x), str(self.y), 
                                                str(self.orientation))
    

       
    # --------
    # move: 
    #   
    def move(self, motion,tolerance=0.001): # Do not change the name of this function

        # ADD CODE HERE
        
        steering=motion[0]
        distance=motion[1]
        
        if abs(steering)>max_steering_angle:
            raise ValueError, 'Exceeding max steering angle'
            
        if distance<0.0:
            raise ValueError, 'Moving backwards is not valid'
        
            
       
        
        res=robot()
        
        res.length=self.length
        res.bearing_noise=self.bearing_noise
        res.steering_noise=self.steering_noise
        res.distance_noise=self.distance_noise
        
        
        steering2=random.gauss(steering,self.steering_noise)
        distance2=random.gauss(distance,self.distance_noise)
        
        turn=(tan(steering2)*distance2)/res.length
        
        if abs(turn)<tolerance:
            res.x=self.x+(distance2*cos(self.orientation))
            res.y=self.y+(distance2*sin(self.orientation))
            res.orientation=(self.orientation+turn)%(2*pi)
            
        else:
            
            radius=distance2/turn
            cx=self.x-(sin(self.orientation)*radius)
            cy=self.y+(cos(self.orientation)*radius)
            res.orientation=(self.orientation+turn)%(2*pi)
            res.x=cx+(sin(res.orientation)*radius)
            res.y=cy-(cos(res.orientation)*radius)
        
        
        return res # make sure your move function returns an instance
                      # of the robot class with the correct coordinates.
    
    # copy your code from the previous exercise
    # and modify it so that it simulates motion noise
    # according to the noise parameters
    #           self.steering_noise
    #           self.distance_noise

    # --------
    # sense: 
    #    
    def sense(self,flag): #do not change the name of this function
        Z = []
        
        if (flag==0):
         for i in range(len(landmarks)):
           bearing=atan2(landmarks[i][0]-self.y,landmarks[i][1]-self.x)-self.orientation
           bearing=bearing%(2*pi)
           Z.append(bearing)
        
        else:
         for i in range(len(landmarks)):
           bearing=random.gauss(atan2(landmarks[i][0]-self.y,landmarks[i][1]-self.x)-self.orientation,self.bearing_noise)
           bearing=bearing%(2*pi)
           Z.append(bearing)   

        # ENTER CODE HERE
        # HINT: You will probably need to use the function atan2()

        return Z #Leave this line here. Return vector Z of 4 bearings.

    # copy your code from the previous exercise
    # and modify it so that it simulates bearing noise
    # according to
    #           self.bearing_noise

    

# --------
#
# extract position from a particle set
# 

def get_position(p):
    x = 0.0
    y = 0.0
    orientation = 0.0
    for i in range(len(p)):
        x += p[i].x
        y += p[i].y
        # orientation is tricky because it is cyclic. By normalizing
        # around the first particle we are somewhat more robust to
        # the 0=2pi problem
        orientation += (((p[i].orientation - p[0].orientation + pi) % (2.0 * pi)) 
                        + p[0].orientation - pi)
    return [x / len(p), y / len(p), orientation / len(p)]

# --------
#
# The following code generates the measurements vector
# You can use it to develop your solution.
# 


def generate_ground_truth(motions):

    myrobot = robot()
    myrobot.set_noise(bearing_noise, steering_noise, distance_noise)

    Z = []
    T = len(motions)

    for t in range(T):
        myrobot = myrobot.move(motions[t])
        Z.append(myrobot.sense())
    #print 'Robot:    ', myrobot
    return [myrobot, Z]

# --------
#
# The following code prints the measurements associated
# with generate_ground_truth
#

def print_measurements(Z):

    T = len(Z)

    print 'measurements = [[%.8s, %.8s, %.8s, %.8s],' % \
        (str(Z[0][0]), str(Z[0][1]), str(Z[0][2]), str(Z[0][3]))
    for t in range(1,T-1):
        print '                [%.8s, %.8s, %.8s, %.8s],' % \
            (str(Z[t][0]), str(Z[t][1]), str(Z[t][2]), str(Z[t][3]))
    print '                [%.8s, %.8s, %.8s, %.8s]]' % \
        (str(Z[T-1][0]), str(Z[T-1][1]), str(Z[T-1][2]), str(Z[T-1][3]))

# --------
#
# The following code checks to see if your particle filter
# localizes the robot to within the desired tolerances
# of the true position. The tolerances are defined at the top.
#

def check_output(final_robot, estimated_position):

    error_x = abs(final_robot.x - estimated_position[0])
    error_y = abs(final_robot.y - estimated_position[1])
    error_orientation = abs(final_robot.orientation - estimated_position[2])
    error_orientation = (error_orientation + pi) % (2.0 * pi) - pi
    correct = error_x < tolerance_xy and error_y < tolerance_xy \
              and error_orientation < tolerance_orientation
    return correct



def particle_filter(motions, measurements, N=500): # I know it's tempting, but don't change N!
    # --------
    #
    # Make particles
    # 

    p = []
    for i in range(N):
        r = robot()
        r.set_noise(bearing_noise, steering_noise, distance_noise)
        p.append(r)

    # --------
    #
    # Update particles
    #     

    for t in range(len(motions)):
    
        # motion update (prediction)
        p2 = []
        for i in range(N):
            p2.append(p[i].move(motions[t]))
        p = p2

        # measurement update
        w = []
        for i in range(N):
            w.append(p[i].measurement_prob(measurements[t]))

        # resampling
        p3 = []
        index = int(random.random() * N)
        beta = 0.0
        mw = max(w)
        for i in range(N):
            beta += random.random() * 2.0 * mw
            while beta > w[index]:
                beta -= w[index]
                index = (index + 1) % N
            p3.append(p[index])
        p = p3
    
    return get_position(p)