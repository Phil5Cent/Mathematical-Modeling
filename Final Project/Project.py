#Features:
#Genetic Algorithm every number of timesteps and upon a split, country does not need to die.
#Probability Distribution of behaviors, ex: 0.4 aggressive, 0.4 defensive, 0.2 passive, 0 colonizing
#Associated actions: attack (prioritizes enemies? prioritizes weak? gradual process?), Defensive: Don't engage, but attack those who attacked allies? 
#Limited resources to be fought over.
#Increase chance of splitting depending on resources
#Cohesion? or morale of the nations? -> constant attacking reduces morale, increasing chance of nation split?, alliances reduce morale (or maybe contribute to the max size penalty?
#Alliances?




#Things that should be strongly considered to implement
#Possibility of Predator missing (energy cost for missing, makes hunting less cheat codey)
#Prey has age limit to reproduce???
#
#What's gonna stop predator from eating all the resources?

#There should be an energy drain like in real life, not infinite energy generation?
import random
import matplotlib.pyplot as plt
import string

class Node:

    Max_age = 50
    Max_resources = 60
    Communication = 1
    Attack_energy = 0.15
    Stress_limit = 20
    verbose=True
    iter=0


    def __init__(self, name = None, node_faction = None, behavior = {"Aggressive": 0.3, "Defensive": 0.3, "Passive": 0.4}, message="Hey there", energy = 5, resources = 20, age=0, allies=[], reboots=0, militarized=False, stress=0):
        
        #Spammed .copys to prevent Nodes from sharing mutable information
        self.stress = stress
        self.behavior = behavior.copy()
        self.reboots = reboots
        self.message = message
        self.energy = energy
        self.resources = resources
        self.age = age
#        self.target = target
        self.allies = allies.copy()
        self.militarized = militarized
        self.last_action = "birthed"

        if name is None:
            self.name = str(id(self))[-4:]
        else:
            self.name = name

        if node_faction in Factions: #if faction is preassigned, add this to self info and add name to faction members
            self.faction = node_faction
            for faction in Factions:
                if faction == self.faction:
                    faction.members.append(self)

        else: #if faction is not preassigned, or preassigned incorrectly, create its own solo faction
            self.faction = Faction(name=self.name+" faction", members=[self])
            Factions.append(self.faction)

        return

    def __str__(self):
        return(f"Name: {self.name}, Faction: {self.faction.name}, Behavior: {self.behavior}, Energy: {round(self.energy,2)}, Resources: {self.resources}, Age: {self.age}")

    def timestep(self): #Timestep

        self.update()
        self.age += 1




        # if self.resources/self.Max_resources > random.random():
        #     self.split()


        #if self.age/self.Max_age > random.random():
        #    print("Died of old age")
        #    self.energy = 0



        # IF stress is high or you are old, and (the faction is  not high energy or resources are very high)
        age_roll = self.age*(random.random()*random.random())
        resource_roll = self.resources*random.random()
        if ((self.stress>self.Stress_limit) or (age_roll > self.Max_age)) and ((self.energy < 0.75*self.resources and self.resources>5) or (resource_roll > self.Max_resources)):
            self.stress-=self.Stress_limit/2
            self.age-=self.Max_age/2
            self.split()

        #150
        gradual_mutation_roll = self.age*(random.random()*random.random())/2
        if gradual_mutation_roll>self.Max_age:
            new_behavior = self.mutate_behavior(degree=0.01)
            self.age-=10
            self.behavior=new_behavior

        self.update()

    def update(self): #Run after each action or through timestep, handles events when parameters match


        if self.stress < 0: #stress minimizes at 0
            self.stress=0

        if self.energy > self.resources: #energy caps out at resource amount
            self.energy = self.resources
                
        if self.resources <= 0:
            raise Exception("Born with no resources")
            print(f"No resources: {self}")
#            self.Population[self.type] -= 1
            Nodes.remove(self)
            
        elif self.energy <= 0:
            if Node.verbose: print(f"Died: {self}")
#            self.Population[self.type] -= 1
            self.faction.members.remove(self)
            self.faction.update()
            self.resources=0
            update_agent_history(Node.iter+1, dead_node=self)
            Nodes.remove(self)
        
    def action(self):

        self.update()
        self.faction.update()

        decision = self.behavior_decision()

        if Node.verbose: print(f"{self.name} ({self.faction.name}) decision: {decision}")

        getattr(self, decision)()

        self.update()
        self.faction.update()

        self.timestep()

    def behavior_decision(self):

        decision = random.choices(list(self.behavior.keys()), weights=list(self.behavior.values()))[0].lower()
        
        return decision

    def aggressive(self):
        
        self.stress+=1
        self.militarized = True
        if self.energy >= self.resources/4: #If you have a reasonable amount of energy to pursue these actions
            

            if self.faction.target_factions: #if there are target factions proceed
                
                self.last_action = "attack"


                if Node.verbose: print(self.name + " attacking faction target")
                
                faction_choice = random.choice(self.faction.target_factions)

                if not faction_choice.members:
                    self.faction.update()
                    raise Exception("Enemy faction has no members?")

                
                enemy = random.choice(faction_choice.members)

                if enemy in Nodes: #attacks a target faction's member
                    self.attack(enemy)
                else:
                    raise Exception("target faction has no living members?")

            else: #if there are no target factions:


         
                if self.faction.vote(author=self, behaviors=["aggressive"], threshold=0.75): #If vote passes to behave aggressively, then pick a target and attack
                    
                    self.last_action = "War Declaration"

                    if Node.verbose: print(self.name + " passed vote to declare war")

                    target_options = [agent for agent in Nodes if agent not in self.faction.members] #gets logical targets (non-allies and not itself)   

                    if target_options: #if targets exist
                        
                        enemy = random.choice(target_options)
                        enemy_faction = enemy.faction #get faction of a random target

                        self.faction.target_factions.append(enemy_faction) #declare war on that faction THIS LINE ADDS ENEMIES TO EVERYONE FOR SOME REASON
                        enemy_faction.target_factions.append(self.faction) #declare mutual war
                        
                        if Node.verbose: print("Declaration of war against " + enemy_faction.name)

                        self.attack(enemy)


                    else:
                        if Node.verbose: print("No targets for war declaration available, resting")
                        self.rest(multiplier=0.5)
                else:
                    if random.random() < 0.2: #disagreement results in chance of breaking alliance

                        if Node.verbose: print(self.name + " got pissed that their war vote failed and left the faction: " + self.faction.name)
                        self.last_action = "alliance broken"
                        self.break_alliance()
                    else:
                        if Node.verbose: print(self.name + " will rest since war vote failed")
                        self.rest(multiplier=0.5)

        else:
            if Node.verbose: print(self.name + " has too little energy to pursue aggression")
            self.rest(multiplier=0.5)

    def break_alliance(self):

        self.last_action = f"Leave Faction {self.faction.name}"
        self.faction.members.remove(self) #removes self from current faction
        # if ~self.faction.members: #If the faction is now empty, delete it
        self.reboots += 1
        new_faction = Faction(name=self.name+f"({str(self.reboots)}) faction", members=[self]) #creates a joins a new faction
        Factions.append(new_faction)
        self.faction = new_faction

    def defensive(self):
        
        self.stress +=1
        self.militarized = True
        if (self.energy >= self.resources/2): #If you have a reasonable amount of energy to pursue these actions and allies
            
            if self.faction.target_factions: #if there are target factions proceed and attack enemies
                
                self.last_action = "defend"
                
                faction_choice = random.choice(self.faction.target_factions)
                
                if not faction_choice.members:
                    self.faction.update()
                    raise Exception("Enemy faction has no members?")

                enemy = random.choice(faction_choice.members)


                #enemy = random.choice(random.choice(self.faction.target_factions).members)
                if Node.verbose: print(self.name + " is attacking faction enemy")

                if enemy in Nodes: #attacks a target faction's member
                    self.attack(enemy)
                    
                    
                else:
                    raise Exception("target faction has no living members?")
                

            elif self.faction.vote(author=self, behaviors=["defensive"], threshold=1): #If vote passes to ally, then attempt an alliance
                        
                if Node.verbose: print(self.name + " passed unanimous vote for alliance")

                self.last_action = "alliance"

                target_options = [agent for agent in Nodes if agent not in self.faction.members] #gets logical targets (non-allies and not itself and non-enemies)   

                if target_options: #if targets exist
                    
                    alliance_faction = random.choice(target_options).faction #get faction of a random target
                    if alliance_faction.vote(behaviors=["defensive","passive"], threshold=1): #checks if potential alliance also agrees
                        if Node.verbose: print(f"{alliance_faction.name} unanimously accepted")
                        self.merge_factions(self.faction, alliance_faction) #merges factions and cleans up
                    
                    else:
                        if Node.verbose: print(f"{alliance_faction.name} declined, so {self.name} will rest")
                        self.rest(multiplier=0.5)

                else:
                    if Node.verbose: print(f"No one to ally, so {self.name} will rest")
                    self.rest(multiplier=0.5)


            else:

                if Node.verbose: print(f"no targets or unanimous desire for alliance, so {self.name} will rest")
                self.rest(multiplier=0.5)

        else: #If not enough energy to pursue aggressive action, then rest

            if Node.verbose: print(self.name + " is too weak to consider aggressively defending their faction")
            self.rest(multiplier=0.5)

    #@staticmethod
    def merge_factions(self, core_faction, merging_faction):
        
        if Node.verbose: print(f"{merging_faction.name} has joined {core_faction.name}")
        self.last_action = f"ally with {merging_faction.name}"
        #print(merging_faction.members)
        for member in merging_faction.members:
            #print(member.name)
            core_faction.members.append(member) #adds new members to the core faction
            member.faction = core_faction #correctly sets member parameters
            #merging_faction.members.remove(member) #removes members from entries in the merging_faction

        merging_faction.members = []
        merging_faction.update() #Gets the merging_faction to effectively destroy itself
        core_faction.update()
        

        if Node.verbose: print(core_faction.members)
        #Rather than handling the complications of targets now being deleted here, I think it should be done in an update pass of the faction?

    def passive(self):
    
        if Node.verbose: print(f"Decision to remain passive, {self.name} will get good rest")
        self.rest(multiplier=1)

    def split(self): #Action, creates a new type
        
        if Node.verbose: print(self.stress)

        resource_loss = round(self.resources*random.random()*0.5,2)+1

        energy_ratio = self.energy/self.resources
        
        self.resources -= resource_loss

        
            
        if self.resources < 0:
            raise Exception("Split occurred but the minimum resource threshold was not met")

        new_behavior = self.mutate_behavior(degree=1)

        #Nodes.append(Node(name = self.name[:7].replace(' ', '') + self.name[-2:].replace(' ', '') + ''.join(random.choices(string.ascii_uppercase, k=2)), behavior = new_behavior, resources=resource_loss, energy=resource_loss*energy_ratio))
        Nodes.append(Node(name = self.name + ''.join(random.choices(string.ascii_letters, k=2)), behavior = new_behavior, resources=resource_loss, energy=resource_loss*energy_ratio))


        # self.last_action = f"Leave Faction {self.faction.name}"
        # self.faction.members.remove(self) #removes self from current faction
        # # if ~self.faction.members: #If the faction is now empty, delete it
        # self.reboots += 1
        # new_faction = Faction(name=self.name+f"({str(self.reboots)}) faction", members=[self]) #creates a joins a new faction
        # Factions.append(new_faction)
        # self.faction = new_faction


        # Nodes.append(Node(type=str(self.type+'_'+''.join(random.choices(string.ascii_uppercase, k=3))), energy=self.energy//3, resources=self.resources // 2))
        # self.energy = self.energy//3
        # self.resources -= self.resources // 2

        # self.timestep()
        
        return

    def mutate_behavior(self, degree=1):

        new_behavior = self.behavior.copy()

        values = list(self.behavior.values())

        if len(values)>3: raise Exception("More than 3 behaviors not currently supported by mutate")

        for value_index in range(len(values[:-1])):

            change = random.random()*0.3*degree-0.15*degree

            if values[value_index] + change > 1:
                values[value_index] = (values[value_index] + 1)/2

            elif values[value_index] + change < 0:
                values[value_index] = (values[value_index] + 0)/2
            
            else:
                values[value_index] += change

            values[value_index] = round(values[value_index],3)

        values[2] = round(1 - sum([entry for entry in values[:-1]]), 3)

        #Very rudamentary and two value limited, but I'll leave it for now to get stuff done
        if values[2]<0:
            values[0] += values[2]/2
            values[1] += values[2]/2
            values[2] = 0

        if values[2]>1:
            values[0] -= (values[2]-1)/2
            values[1] -= (values[2]-1)/2
            values[2] = 1


        for index, behavior in enumerate(list(self.behavior.keys())):

            new_behavior[behavior] = values[index]

        return new_behavior

    def rest(self, multiplier=1): #Action

        if (self.energy >= self.resources/2) and (self.faction.target_factions): #If you have a reasonable amount of energy to pursue these actions and allies
            
            self.stress += 1

            self.last_action = "Defend (rest)"
            
            faction_choice = random.choice(self.faction.target_factions)
            
            if not faction_choice.members:
                self.faction.update()
                raise Exception("Enemy faction has no members?")

            enemy = random.choice(faction_choice.members)


            #enemy = random.choice(random.choice(self.faction.target_factions).members)
            if Node.verbose: print(self.name + " is attacking faction enemy")

            if enemy in Nodes: #attacks a target faction's member
                self.attack(enemy)
            else:
                raise Exception("attacking, but enemy is not in Nodes list?")
                    
        else:
            
            self.stress-=multiplier #For every attack, you have to rest to maintain low stress
            self.militarized = False
            self.last_action = f"Rest {str(multiplier)}"
            self.energy += (self.resources*0.1)*multiplier

        return

    def attack(self, target):

        if Node.verbose: print(f'{self.name} attacking {target.name}')
        self.last_action = f"attack {target.name}"

        multiplier = 1
        if not target.militarized:
            multiplier = 1.5

        self.energy -= self.resources*0.15

        target.energy -= self.resources*0.1*multiplier

        if target.energy <= 0:
            self.resources += target.resources
            

        target.update()

        self.timestep()

        



        return

    def shout(self): #Testing


        print(self.message)
        
        # for node in Nodes:
        
        #    print(node.type)

        return



class Faction:

    verbose=False

    def __init__(self, name, members, target_factions = []):
        self.name = name
        self.members = members

        if type(self.members) != list: print(type(self.members)); raise Exception("faction created with members as object instead of list")

        self.target_factions = target_factions.copy()
    
    def update(self):
        #print(Factions)
        #print("self:")
        #print(self)

        for enemy in self.target_factions: #look through all of this faction's enemies
                if not enemy.members: #If an enemy faction has no members, remove it as an enemy
                    enemy.update()
                    self.target_factions.remove(enemy)
                    


        if not self.members: #If no members are in the faction, 

            if self in Factions: #If this faction is in the list
                Factions.remove(self) #Remove itself from the list

            # else:
            #     print("bruhbruhbruh")
            #     print("bwieh")        
            for faction in Factions: #Iterate through every faction
                if self in faction.target_factions: #Check if this faction is anyone's enemy and remove itself as an enemy.
                    faction.target_factions.remove(self) #Remove itself as a target of any other faction

    def vote(self, behaviors, author=None, threshold=0.5):
        
        if author is None:
            votes=0
            total=0
        else:
            votes=1
            total=1

        for member in self.members:
            if member != author:
                total+=1
                if member.behavior_decision() in behaviors:
                    votes+=1 
            
        if Faction.verbose: print(f"faction: {self.name}, vote: {round(votes/total,3)}")

        if votes/total>=threshold:
            return True
        else:
            return False

    # def unanimous_vote(self, behaviors):
        
    #     for member in self.members:
    #         if member.behavior_decision() not in behaviors:
    #             print("Unanimous vote failed")
    #             return False
    #     return True




#updated issues:
"""


Currently, vibing and healing will gain troops faster than attacking can remove troops. There should be a militarization bonus if defending or attacking?

Every so many iterations a random node joins, which might be a better representation and normalizer?
"""




#ida = 0
Nodes = []
Factions = [] #Faction as dicionary with: members, target factions

# Nodes.append(Node(name = "Stoner1  ", behavior = {"Aggressive": 0.01, "Defensive": 0.39, "Passive": 0.6}, resources=70)) #Mostly Passive
# Nodes.append(Node(name = "Stoner2  ", behavior = {"Aggressive": 0.01, "Defensive": 0.3, "Passive": 0.69}, resources=20)) #Mostly Passive
# Nodes.append(Node(name = "Stoner3  ", behavior = {"Aggressive": 0.01, "Defensive": 0.3, "Passive": 0.69}, resources=50)) #Mostly Passive

# Nodes.append(Node(name = "Switkes", behavior = {"Aggressive": 0, "Defensive": 0.7, "Passive": 0.3}))
# Nodes.append(Node(name = "Philip", behavior = {"Aggressive": 1, "Defensive": 0.0, "Passive": 0.0}))



Nodes.append(Node(name = "Wallnut  ", behavior = {"Aggressive": 0.1, "Defensive": 0.7, "Passive": 0.2})) #Mostly Defensive
Nodes.append(Node(name = "Flower  ", behavior = {"Aggressive": 0.7, "Defensive": 0.2, "Passive": 0.1}))#, resources=100)) #Mostly Aggressive
Nodes.append(Node(name = "Stoner  ", behavior = {"Aggressive": 0.1, "Defensive": 0.3, "Passive": 0.6})) #Mostly Passive
Nodes.append(Node(name = "Karen  ", behavior = {"Aggressive": 0.5, "Defensive": 0.4, "Passive": 0.1})) #Aggressive and Defensive
Nodes.append(Node(name = "Hermit  ", behavior = {"Aggressive": 0.1, "Defensive": 0.5, "Passive": 0.4})) # Defensive and Passive
Nodes.append(Node(name = "Passive-Aggressive  ", behavior = {"Aggressive": 0.4, "Defensive": 0.1, "Passive": 0.5})) # Aggressive and Passive

Nodes.append(Node(name = "Pal  ", behavior = {"Aggressive": 0.3, "Defensive": 0.3, "Passive": 0.4})) #Balanced Passive
Nodes.append(Node(name = "Buddy  ", behavior = {"Aggressive": 0.3, "Defensive": 0.4, "Passive": 0.3})) #Balanced Defensive
Nodes.append(Node(name = "Mister  ", behavior = {"Aggressive": 0.4, "Defensive": 0.3, "Passive": 0.3})) #Balanced Aggressive


# print(Nodes[0].behavior)
# print(Nodes[0].mutate_behavior(degree=0.05))
# print("nope")



def update_agent_history(iter, dead_node=None):

        #This handles nodes not being skipped bc they were removed before the end of iteration count
        if (dead_node is not None): #If a specific now dead node is being fed in
            
            Agent_history.setdefault(dead_node.name,{"iteration":[], "resources":[], "energy":[], "faction":[], "last_action":[]})

            Agent_history[dead_node.name]["iteration"].append(iter)
            Agent_history[dead_node.name]["resources"].append(dead_node.resources)
            Agent_history[dead_node.name]["energy"].append(dead_node.energy)
            Agent_history[dead_node.name]["faction"].append(dead_node.faction.name)
            Agent_history[dead_node.name]["last_action"].append(dead_node.last_action)

        else:
            for agent in Nodes: #Right here, add an if statement to check if that iteration already exists, if so it was manually written and called on the node's death
                
                Agent_history.setdefault(agent.name,{"iteration":[], "resources":[], "energy":[], "faction":[], "last_action":[]})
    
                Agent_history[agent.name]["iteration"].append(iter)
                Agent_history[agent.name]["resources"].append(agent.resources)
                Agent_history[agent.name]["energy"].append(agent.energy)
                Agent_history[agent.name]["faction"].append(agent.faction.name)
                Agent_history[agent.name]["last_action"].append(agent.last_action)

def agents_play():

    random.shuffle(Nodes) #Makes order of actions random each time
    for agent in Nodes: #Make every living agent act
        agent.action()




Faction_history = {}
Faction_resources = []
Agent_history = {}
Last_iteration=0



def run_it(steps=100, verbose=True):

    update_agent_history(iter=0)
    Node.verbose=verbose
    Faction.verboes=verbose

    for iter in range(steps): #Allow this many timesteps of actions

        Node.iter=iter



        agents_play()
    
        

        update_agent_history(iter+1)

        

            

        print(f"\nend of iteration {iter+1}\n")
        
        #    print(F"{faction.name} has members {faction.members} and enemies {faction.target_factions}")
        



def agent_plot(steps, factor = "energy", average=True, net=True, cutoff=0, duration_min=0):
#    x = range(0,len(Population_Tracker))

    plt.figure(figsize=(16,12))
    #lines=[]
    factor=factor.lower()

    num_agents_graphed = 0

    # averaging = {"iterations":[0]*(Last_iteration+2), "value":[0]*(Last_iteration+2)}
    for agent_name,agent_data in Agent_history.items():
        #print(faction_name)
        # print(faction_data)

        iterations = agent_data["iteration"]
        factor_data = agent_data[factor]


        if iterations[-1]>=cutoff and iterations[-1]-iterations[0]>=duration_min:
            


            num_agents_graphed += 1

            for i in range(len(iterations)): #iterating through the number of iterations that each faction existed
                
    #            iterations[i] # ith iteration number
                iteration_number = iterations[i]

                # averaging["iterations"][iteration_number] += 1 #adds one to the corresponding occurence slot on averaging
                # averaging["value"][iteration_number] += factor_data[i]#adds the value to the corresponding occurence slot on value

                
            #averaging["iterations"].extend(iterations)
            #averaging["value"].extend(factor_data)

            #plt.plot(iterations, factor_data)
            #lines.append(plt.plot(iterations, factor_data, label=faction_name))

            current_line = plt.plot(iterations, factor_data, label=agent_name)

            #print(lines[-1][-1])

            
            if iterations[-1] == steps:
                
                plt.plot(iterations[-1], factor_data[-1], marker='>', markersize=6, color=current_line[-1].get_color())#, color='rb)
            else:
                plt.plot(iterations[-1], factor_data[-1], marker='x', markersize=5, color=current_line[-1].get_color())#, color='rb)
            
            plt.plot(iterations[0], factor_data[0], marker='s', markersize=5, color="black")
            
            
        #plt.plot(Faction_history)
        #history = []
 #       for cycle in Population_Tracker:        
  #          history.append(cycle.get(species,0))
        
#        plt.plot(x, history, label=species)

    #Divide by zero error for areas where the plot is ignored
    # if average or net: averages = [b / a for b, a in zip(averaging["value"], averaging["iterations"])]
    
    # if average: plt.plot(range(len(averages)), averages, linestyle='dotted', label="Average", color="black")
    # if net: plt.plot(range(len(averaging["value"])), averaging["value"], linestyle=(0,(3, 5)), label="Net", color="black")
    plt.xlabel('Iteration')
    plt.ylabel(factor)
    plt.title('Agents Over Time')
    if num_agents_graphed < 15: plt.legend(loc='upper left')
    plt.savefig('Agent_Figure.png', dpi=500)
    #plt.show()
    #print(lines)

# Agent_history[agent.name]["iteration"].append(iter)
# Agent_history[agent.name]["resources"].append(agent.resources)
# Agent_history[agent.name]["energy"].append(agent.energy)
# Agent_history[agent.name]["faction"].append(agent.faction.name)
# Agent_history[agent.name]["last_action"].append(agent.last_action)




#SAVING DATA


 


"""
Observations:

The default aggression numbers are REALLY HIGH

Even with crazy aggression, stability eventually emerges

Two types of behaviors emerge: 

1.) One dominant faction with repeated rebellions and new rule

2.) Multiple stable factions that adapt to no longer be aggressive

"""


#calling data viewing functions


steps = 100000
run_it(steps=steps, verbose=False)
agent_plot(factor="energy", steps=steps, average=False, net=False, duration_min=steps/1000)#0)#steps/40)#0



with open('Results.txt', 'a') as file:
    for i, agent in enumerate(Nodes):
        print(agent)
        writing_data="("+agent.name+", "+agent.faction.name+", "+str(agent.age)+")"
        if i>0:
            writing_data = "  +  "+writing_data
        file.write(writing_data)
        
    file.write('\n')



writing_Faction_history = str(Agent_history).replace("},", "}\n\n").replace("{","{\n").replace("],", "],\n")
with open('Faction_Run.txt', 'w') as file:
    file.write(writing_Faction_history)


writing_Agent_history = str(Agent_history).replace("},", "}\n\n").replace("{","{\n").replace("],", "],\n")
with open('Agent_Run.txt', 'w') as file:
    file.write(writing_Agent_history)


print('done')

# with open('Temp.txt', 'a') as file:
#     writing_data="("
#     for i, agent in enumerate(Nodes):
        
#         name = agent.name[:3]
#         if name not in writing_data: writing_data+=name + ","
    
#     if writing_data[-1] == ",": writing_data= writing_data
#     writing_data+=")\n"
#     file.write(writing_data)
