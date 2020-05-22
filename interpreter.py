import sys
import numpy as np 
import string
import math
import os
os.system("clear")

#check if a string is an int or a float 
def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

#parse the expression to create an abstract syntax tree 
def parse(expression):

    #first, separate expression into components
    expression = expression.replace('(', ' ( ')
    expression = expression.replace(')', ' ) ')

    #then, split expression into separate elements
    expr_array_intermediate = expression.split(' ')

    #remove '' from expr_array_intermediate 
    expr_array = [x for x in expr_array_intermediate if x != '']

    #if it doesn't start with '(', it's not a valid lisp expression
    if expr_array[0] != '(' and len(expr_array) != 1:
        sys.exit("Invalid expression.\n")

    #check for unbalanced brackets '(', ')'
    left_bracket_counter = 0
    right_bracket_counter = 0
    x = 0
    while x < len(expr_array):
        if expr_array[x] == '(':
            left_bracket_counter += 1
        elif expr_array[x] == ')':
            right_bracket_counter += 1
        x += 1 
    if left_bracket_counter != right_bracket_counter:
        sys.exit("Unbalanced brackets.\n")

    #go through expr_array and create abstract syntax tree 
    x = 0
    while x < len(expr_array):

        #start parsing 
        #we want to put each sub-expression inside an array 
        #keep going until we see the first ')', which indicates the end of a sub-expression 
        if expr_array[x] == ')':

                #this will store that sub-expression 
                #and will eventually store our whole parsed expression!
                expression = [] 

                #remove that ')' from the expression (since we've parsed it!)
                del expr_array[x] 

                #look at previous element 
                x -= 1

                #as long as we're still looking at that sub-expression
                while x >= 0 and expr_array[x] != '(': 

                    #if element is a number, it stays a number
                    #otherwise, it's a symbol 
                    """
                    #do lstrip('-') to also account for negative numbers
                    if str(expr_array[x]).lstrip('-').isnumeric() == True: 
                        expr_array[x] = int(expr_array[x])
                    """
                    if is_number(str(expr_array[x])):
                        try: #see if the number (int/float) can be converted into int 
                            expr_array[x] = int(expr_array[x])
                        except: #if error, convert it into a float 
                            expr_array[x] = float(expr_array[x])

                    #since we're reading the sub-expression backwards, insert each element at position 0 (beginning of list)
                    expression.insert(0, expr_array[x])
                
                    #remove that element from the expression (since we've parsed it!)
                    del expr_array[x]

                    #go backwards through the expression until we reach the end of the sub-expression (indicated by '(')
                    x -= 1

                #delete the '(' of that sub-expression from the expression 
                del expr_array[x] 

                #add parsed sub-expression (list) in place of non-parsed sub-expression to its position (x) in the list 
                expr_array.insert(x, expression)

        #go to the next element of the expression 
        x += 1

    #print("\nParsed expression :", expression, "\n")
    return expression

#evaluate the expression 
#currently supports +, -, *, /, =, <, <=, >, >=, exp, sqrt, max, min, abs, if 
def evaluate(expression, var_dict):

    #if it is a list 
    if isinstance(expression, list):
    
        #separating expression into variable that stores the function and array that stores the arguments
        function, *args = [evaluate(item, var_dict) for item in expression]

        #update the values in args by checking the dictionary to see if symbols have been assigned values 
        for i in range(0, len(args)):
            if args[i] in var_dict:
                args[i] = var_dict[args[i]]

        #defining addition operation 
        if function == '+':
            return sum(args)

        #defining subtraction operation (if only one element x, return -x)
        elif function == '-':
            if len(args) == 1: 
                return -args[0]
            else:
                difference = args[0]
                for i in range(1, len(args)):
                    difference -= args[i]
                return difference

        #defining multiplication operation 
        elif function == '*':
            return np.prod(args)

        #defining division operation (if only one element x, return 1/x)
        elif function == '/':
            if len(args) == 1: 
                return 1/args[0]
            else:
                quotient = args[0]
                for i in range(1, len(args)):
                    quotient /= args[i]
                return quotient 

        #defining = operation to check if the numbers in a list are equal 
        elif function == '=':
            return args[1:] == args[:-1]

        #defining < operation to check if args[0] < args[1] < ... < args[n]
        elif function == '<':
            for i in range(0, len(args)-1):
                if args[i] >= args[i+1]:
                    return False
            return True

        #defining <= operation to check if args[0] <= args[1] <= ... <= args[n]
        elif function == '<=':
            for i in range(0, len(args)-1):
                if args[i] > args[i+1]:
                    return False
            return True

        #defining > operation to check if args[0] > args[1] > ... > args[n]
        elif function == '>':
            for i in range(0, len(args)-1):
                if args[i] <= args[i+1]:
                    return False
            return True

        #defining >= operation to check if arg[0] >= args[1] >= ... >= args[n]
        elif function == '>=':
            for i in range(0, len(args)-1):
                if args[i] < args[i+1]:
                    return False
            return True

        #defining the exponent operation, which only works for two arguments 
        elif function == 'expt' and len(args) == 2:
            return args[0]**args[1]

        #defining the sqrt operation
        elif function == 'sqrt' and len(args) == 1:
            return math.sqrt(args[0])

        #defining the max operation
        elif function == 'max':
            return max(args)

        #defining the min operation
        elif function == 'min':
            return min(args)

        #defining the abs operation
        elif function == 'abs' and len(args) == 1:
            return abs(args[0])

        #defining the if operation (if test conseq1 conseq2) => if test = True, it returns conseq1, otherwise it returns conseq2 
        elif function == 'if' and len(args) == 3:
            if args[0] == True:
                return args[1]
            return args[2]

        #defining the list operation, which just returns the arguments as a list 
        elif function == 'list':
            return args

        #defining the define operation, which assigns a value to a symbol (stored in a dictionary)
        elif function == 'define':
            x = args[0]
            var_dict[x] = args[1]
            return var_dict[x]
        
        #defining the begin operation, which calculates a sequence of expressions and returns the last result 
        elif function == 'begin':
            return args[-1]

        #if operation is not supported 
        else:
            sys.exit("Unable to evaluate expression.\n")

    #if it isn't a list (it's an atom!), then just return it 
    else:
        try:
            return var_dict[expression] #check if it's got a value stored in the dictionary 
        except:
            return expression

#ask user for lisp expression 
expression = input("babylisp> ")

while expression != '(quit)':

    #dictionary used to store values of symbols 
    #reset the dictionary before each new expression 
    var_dict = {}

    #parse and evaluate the expression 
    result = evaluate(parse(expression), var_dict)
    print(result)

    expression = input("\nbabylisp> ")

    if expression == '(quit)':
        print("bye.\n")