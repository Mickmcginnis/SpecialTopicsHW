import picos as pic
from picos import RealVariable
from copy import deepcopy
from heapq import *
import heapq as hq
import numpy as np
import itertools
import math
counter = itertools.count() 

class BBTreeNode():
    def __init__(self, vars = [], constraints = [], objective='', prob=None):
        self.vars = vars
        self.constraints = constraints
        self.objective = objective
        self.prob = prob

    def __deepcopy__(self, memo):
        '''
        Deepcopies the picos problem
        This overrides the system's deepcopy method bc it doesn't work on classes by itself
        '''
        newprob = pic.Problem.clone(self.prob)
        return BBTreeNode(self.vars, newprob.constraints, self.objective, newprob)
    
    def buildProblem(self):
        '''
        Bulids the initial Picos problem
        '''
        prob=pic.Problem()
   
        prob.add_list_of_constraints(self.constraints)    
        
        prob.set_objective('max', self.objective)
        self.prob = prob
        return self.prob

    def is_integral(self):
        '''
        Checks if all variables (excluding the one we're maxing) are integers
        '''
        for v in self.vars[:-1]:
            if v.value == None or abs(round(v.value) - float(v.value)) > 1e-4 :
                return False
        return True

    def branch_floor(self, branch_var):
        '''
        Makes a child where xi <= floor(xi)
        '''
        n1 = deepcopy(self)
        n1.prob.add_constraint( branch_var <= math.floor(branch_var.value) ) # add in the new binary constraint

        return n1

    def branch_ceil(self, branch_var):
        '''
        Makes a child where xi >= ceiling(xi)
        '''
        n2 = deepcopy(self)
        n2.prob.add_constraint( branch_var >= math.ceil(branch_var.value) ) # add in the new binary constraint
        return n2


    def bbsolve(self):
        '''
        Use the branch and bound method to solve an integer program
        This function should return:
            return bestres, bestnode_vars

        where bestres = value of the maximized objective function
              bestnode_vars = the list of variables that create bestres
        '''

        # these lines build up the initial problem and adds it to a heap
        root = self
        res = root.buildProblem().solve(solver='cvxopt')
        heap = [(res, next(counter), root)]
        # best result of maximized objective function
        bestres = -1e20 # a small arbitrary initial best objective value
        # values of variables for bestres
        bestnode_vars = root.vars # initialize bestnode_vars to the root vars

        while len(heap) > 0:
            _, _, n = hq.heappop(heap)
            try:
                currentres = n.prob.solve(solver="cvxopt")
                print("Objective value: {}".format(n.prob.value))
            except:
                print("Pruned, infeasible solution")
                pass

            if bestres > currentres.value:
                print("Pruned, not better than bestres")
                pass

            elif n.is_integral():
                # bestres = float(n.prob.value)
                bestres = float(n.vars[-1])
                bestnode_vars = [val.value for val in n.vars]
                print("New bestres: {}\nNew bestnode_vars: {}".format(bestres, bestnode_vars))

            else:
                for val in n.vars:
                    if val.value != None and abs(round(val) - float(val)) > 1e-4:
                        hq.heappush(heap, (float(bestres), next(counter), n.branch_floor(val)))
                        hq.heappush(heap, (float(bestres), next(counter), n.branch_ceil(val)))
                        print("Branched")
                        break
        if bestres == -1e20:
            print("No feasible solutions")
        return bestres, bestnode_vars
 
