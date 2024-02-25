#I absolutely would have loved to explore a 2 or 3 dimensional walk with a multitude of variations... 
#But unfortunately I have too much going on right now with classes, work, REUs etc. So, I will have to stick to the basic case.

#Also note, to run this on your pc, you will need to have the matplotlib module installed. 
#If you do not have it installed and want to know how, I would be more than happy to show you.
#This is a very common practice in python, and is a very easy thing to set up. 

#Steps to run the simulation are at the bottom, all that needs to be done is tweaking the numbers within the 'Walk' model.
#All code is annotated and is allegedly comprehensible. 

#importing modules used for plotting and random number generation
import matplotlib.pyplot as plt
import random

# Random Walk Model
class RandomWalk:

    # Initializes the class with appropriate variables
    def __init__(self, threshold, trials, steps, rand_step_distance):
        
        # Defines Parameters
        self.threshold = threshold
        self.trials = trials
        self.steps = steps
        self.rand_step_distance = rand_step_distance
    
    # Simulates a random walk
    def simulate(self):

        # Creates an empty path variable
        paths = []

        # Iterates through each trial
        for _ in range(self.trials):
            
            # Initializes the path variable, and sets the starting position to 0.
            path = [0]

            # Iterates through each step of a trial
            for _ in range(self.steps):
                
                # Assigns the step distance based on the simulation parameters
                if self.rand_step_distance:
                    step_distance = random.random() + 0.5  #allows steps ranging from distance 0.5 to 1.5
                else:
                    step_distance = 1
                
                # Generates a random number
                step_gen = random.random()

                # Determines whether to step left or right
                if step_gen < self.threshold:
                    path.append(path[-1] + step_distance) #step right
                else:
                    path.append(path[-1] - step_distance) #step left
            
            # Appends the path to the paths list
            paths.append(path)
        
        # Returns the paths variable
        return(paths)
    
    # Plots paths of the data
    def pathplot(self, paths):
        
        # Generates timesteps for graphing
        timesteps = range(self.steps+1)

        # Plots a line for each path
        for path in paths:
            plt.plot(path, timesteps, linestyle = "--", linewidth = 1)

        # Add labels and titles
        plt.xlabel('Position')
        plt.ylabel('Step')
        plt.title(f'Threshold: {self.threshold}, Trials:{self.trials}, Steps:{self.steps}, Random Step Distance: {self.rand_step_distance}', fontsize = 10)
        plt.suptitle('Paths Over Time')

        # Displays the plot
        plt.show()

    # Plots a barplot of the data
    def barplot(self, paths):
        
        # Creates an empty dictionary for counting simulation results
        results = {}

        # Extracts the result from each path
        for path in paths:
            result = round(path[-1]) # Acquires the final position and rounds for proper bar plot

            if result in results:
                results[result] += 1
            else:
                results[result] = 1
        
        # Gets parameters for plotting
        keys = list(results.keys())
        values = list(results.values())


        # Generates bars
        plt.bar(keys, values)

        # Adds labels and titles
        plt.xlabel('Position')
        plt.ylabel('Count')
        plt.title(f'Threshold: {self.threshold}, Trials:{self.trials}, Steps:{self.steps}, Random Step Distance: {self.rand_step_distance}', fontsize=10)
        plt.suptitle('Random Walk Results')

        # Displays the plot
        plt.show()




# Any of the parameters defined can be changed
Walk = RandomWalk(threshold=0.5, trials=10, steps=8, rand_step_distance=False)

# Simulates the paths taken
paths = Walk.simulate()

# Graphs the path plot
Walk.pathplot(paths)

# Graphs the barplot
Walk.barplot(paths)
