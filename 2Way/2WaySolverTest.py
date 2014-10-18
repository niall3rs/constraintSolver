#!/usr/bin/python

# Import modules needed for later
import copy
import sys
import timeit

# Function that returns a dictionary of key-value pairs, where the key signifies the variable in question, and the value is a list representing the domain of values it may take
# Currently assigns the same domain to all variables, as this is the case for graph colouring; would need to be adapted for different problem classes
def assignDomains (variables,domain):
    dom = {}
    for x in variables:
        dom[x] = domain[:]
    return dom

# Function that takes the bi-directional constraints, and returns a tuple of arcs
def generateArcs(constraints):
    arcsList = []
    for c in constraints:
        arcsList.append(c)
        arcsList.append(c[::-1])
    arcs = tuple(arcsList)
    return arcs

# Function to revise an arc with the inequality constraint
# Removes any values from the appropriate list in the 'dom' dictionary that would violate the inequality constraint
def reviseInequality (arc,dom):
    for i in range(len(dom[arc[0]])):
        # Assume there is no support, and the value must be thrown away
        throwAway = True
        for y in dom[arc[1]]:
            # If we find any support, don't throw it away
            if dom[arc[0]][i] != y:
                throwAway = False
        # Set the value to 'None' if no support, so as not to mess with indexing
        if throwAway:
            dom[arc[0]][i] = None
    
    # Filter out the 'None' values
    dom[arc[0]] = [x for x in dom[arc[0]] if x is not None]
    
    # Finally, return False if we've run out of values
    if len(dom[arc[0]]) > 0:
        return True
    else:
        return False

# Function to revise an arc with the equality constraint
# Similar to above, mainly used for testing / comparison with the above function
def reviseEquality (arc,dom):
    for i in range(len(dom[arc[0]])):
        throwAway = True
        for y in dom[arc[1]]:
            if dom[arc[0]][i] == y:
                throwAway = False
        if throwAway:
            dom[arc[0]][i] = None
    dom[arc[0]] = [x for x in dom[arc[0]] if x is not None]
    if len(dom[arc[0]]) > 0:
        return True
    else:
        return False

# Function that prints out the solution, and ends the program
def showSolution(dom):
    print('\nSuccess! Solution is as follows:')
    print(dom)

# Function that prints a message if no solution is found
def noSolution():
    print('\nNo solution found')
    print('')

# Forward checking function
# Recursively calls itself at the next depth level if arc consistent
def forwardCheck(depth,reviseFunction,dom,queue,arcs,constraints,heuristic,hType):

    if hType=='dynamic':
        queue = heuristic(queue,dom,depth)
    elif hType=='static' and depth==0:
        queue = heuristic(queue,constraints)
    
    value = dom[queue[depth]].pop(0)
    leftOver = dom[queue[depth]]
    
    dom[queue[depth]] = [value]
    consistent = True
    
    for arc in arcs:
        if queue[depth]==arc[1] and consistent:
            consistent = reviseFunction(arc,dom)
    
    if consistent:
        if depth == len(queue)-1:
            return True
        else:
            return forwardCheck(depth+1,reviseFunction,dom,queue,arcs,constraints,heuristic,hType)
    
    elif len(leftOver)>0:
            dom[queue[depth]]=leftOver
            return forwardCheck(depth,reviseFunction,dom,queue,arcs,constraints,heuristic,hType)
    else:
        return False

# Function to implement smallest domain first
# Swaps the variable at the current depth in the queue with the future variable with the smallest domain
def sdf(queue,dom,depth):

    # Make a copy of the queue to edit
    newQueue = copy.deepcopy(queue)
    domainList=[]

    # Check all future variables for their domain size
    for i in range(len(newQueue[depth:])):
        domainList.append(0)
        domainList[i]=len(dom[newQueue[depth:][i]])
        
    # Get the correct index
    minIndex = domainList.index(min(domainList))
    
    # Swap the variable with the smallest domain with the variable at the current depth
    # If current depth has the smallest domain, leave as is
    if minIndex>0:
        newQueue[depth],newQueue[depth+minIndex] = newQueue[depth+minIndex],newQueue[depth]
    
    return newQueue

# Function that returns a sorted queue of variables to be assigned according to their degree
def maximumDegree(queue,constraints):
    def degree(variable):
        count = 0
        for const in constraints:
            if variable in const:
                count+=1
        return count
    newQueue = sorted(queue,key=degree,reverse=True)
    return newQueue

# Function that returns a sorted queue of variables to be assigned according to their cardinality
def maximumCardinality(queue,constraints):

    newQueue = []
    
    # Randomly add the first variable
    newQueue.append(queue.pop(0))
    
    # Until the queue is empty, count how many constraints each element shares with those in newQueue
    while len(queue)>0:
        cardList = []
        for i in range(len(queue)):
            cardList.append(0)
            for const in constraints:
                for x in newQueue:
                    if queue[i] in const and x in const:
                        cardList[i]+=1
        
        # Find the index of max cardinality
        maxIndex = cardList.index(max(cardList))
        
        # Move the corresponding variable to newQueue
        newQueue.append(queue.pop(maxIndex))
    
    return newQueue

# Function to rewrtite a function with arguments as function with no arguments
# Used here to pass forwardCheck into the timing function
def wrapper(func, *args):
    def wrapped():
        return func(*args)
    return wrapped

# Main function to initialise the problem, and call the other functions
def main():
    heuristics = [maximumDegree,maximumCardinality,sdf]
    hNames = ['maximum degree','maximum cardinality','smallest domain first']
    
    # Run for all three heuristics
    for h in (0,1,2):
       
        variables = ('x1','x2','x3','x4','x5','x6','x7')
        domain = [1,2,3,4]
        constraints = (('x1','x2'),('x1','x3'),('x1','x4'),('x1','x6'),('x2','x4'),('x2','x5'),('x2','x7'),('x3','x6'),('x3','x4'),('x4','x5'),('x4','x6'),('x4','x7'),('x5','x7'),('x6','x7'))
        queue = []
        dom = assignDomains(variables,domain)
        arcs = generateArcs(constraints)
        
        for var in dom:
            queue.append(var)        
        
        if h==2:
            hType='dynamic'
        else:
            hType='static'
        
        soln = forwardCheck(0,reviseInequality,dom,queue,arcs,constraints,heuristics[h],hType)
        if soln:
            showSolution(dom)
        else:
            noSolution()

if __name__ == '__main__':
    main()
