import random
from utils import *

class speedUp:

    def __init__(self, config):
        self.config = config
        self.generic_questions = []
        self.questions = []

    def constructAQuestion(self, choice_number_index, choices, prompt_arg):
        return {
            "prompt" : self.config["prompt"].format(prompt_arg),
            "choices" : choices,
            "answers" : choice_number_index
        }

    def constructQuestions(self):
        num_questions = self.config["num_questions"]
        choices = self.config["choice_numbers"][:]
        if self.config["include_none_of_the_above"]:
            choices.append("None of the above")

        assert num_questions <= len(choices)

        questions = []
        
        picked_answers = random.sample(range(len(choices)), num_questions)
        for i in range(num_questions):
            cur_answer = picked_answers[i]
            c = [(choices[i], i == cur_answer) for i in range(len(choices))]
            if self.config["shuffle_choices"]:
                random.shuffle(c)
            cur_answer = [i for i in range(len(c)) if c[i][1]][0]
            c = [pair[0] for pair in c]
            
            if type(c[cur_answer]) is int:
                questions.append(self.constructAQuestion(cur_answer, c, int(100/c[cur_answer])))
            else:
                while True:
                    n = random.randrange(5, 96, 5)
                    if n not in c:
                        questions.append(self.constructAQuestion(cur_answer, c, int(100/n)))
                        break
        return {
            "multiple_choice" : questions
        }

    def constructQuestion(self, generic, params):
        loop_bounds, move, degrees = params
        question = []
        print("generic ", repr(generic), "params ", params)
        for statement in generic.body:
            statement = statement.copy()
            if isinstance(statement, ForLoop):
                statement.bounds = loop_bounds
                print("bound is ", statement.bounds)
                statement.statements = self.constructQuestion(statement.statements, params)
            elif isinstance(statement, Move):
                statement.amount = move
            elif isinstance(statement, Turn):
                statement.degrees = degrees
            question.append(statement)
            print("statement is ", statement)

        return Statements(question)

    def constructQuestions(self):
        TURNS = [90, 180, -90]
        MOVES = [1,2,3,-1,-2,-3]
        FOR_LOOP = [(0, 'N'), (0, '2N'), (0, '3')]

        combinations = [(loop_bounds, move, turn) for loop_bounds in FOR_LOOP \
        for move in MOVES for turn in TURNS]
        questions = []
        for question in self.generic_questions:
            for combination in combinations:
                q = self.constructQuestion(question, combination)
                questions.append(q)

        return questions

    def constructGenericQuestions(self):
        inputVals = [TURN, FOR_LOOP, MOVE]
        permutations = [[self.getEmptyStatement(statement) for statement in perm] for perm in self.perms(inputVals) if self.valid_perm(perm)]
        print("permutations ",permutations)
        questions = []
        for perm in permutations:
            if self.valid_perm(perm):
                for i in range(len(perm)):
                    if isinstance(perm[i], ForLoop):
                        questions += self.createForLoops(i, perm)
                        break
        self.generic_questions = questions
        return questions

    def createForLoops(self, index, question):
        output = []
        for j in range(index + 2, len(question) + 1):
            before_loop = question[0:index]
            loop = question[index].copy()
            loop.statements = Statements(question[index + 1: j])
            after_loop = question[j:]
            output.append(Statements(before_loop + [loop] + after_loop))
        return output

    def getEmptyStatement(self, statement_type):
        if statement_type == FOR_LOOP:
            return ForLoop()
        if statement_type == TURN:
            return Turn()
        if statement_type == MOVE:
            return Move()

    def valid_perm(self, perm):
        return perm[-1] != FOR_LOOP

    def perms(self, lst):
        if lst == []:
            return [[]]
        out = []
        for i in range(len(lst)):
            for perm in self.perms(lst[:i] + lst[i + 1:]):
                out += [[lst[i]] + perm]
        return out

class Statements:
    def __init__(self, body = []):
        self.body = body

    def __str__(self):
        output = ""
        for statement in self.body:
            output += f"\n{str(statement)}"
        return output

    def __repr__(self):
        return repr(self.body)

class ForLoop():
    """ 
    Initalize the for loop using bounds and statements

    bounds: a tuple consisting of the lower and upper bound of the for loop
    statements: an array of statements that go into the for loop
    """
    def __init__(self, statements = Statements(), bounds = (0, 'N')):
        self.bounds = bounds
        self.statements = statements

    def __repr__(self):
        # return self.__str__()
        return f"ForLoop({self.bounds}, {repr(self.statements)})"

    def __str__(self):
        body_string = ""
        for statement in self.statements.body:
            body_string += f"\t{statement}\n"
        return f"for i = {self.bounds[0]} to {self.bounds[1]}: \n {body_string.rstrip()}"

    def copy(self):
        return ForLoop(self.statements, self.bounds)

class Move():
    def __init__(self, amount = 0):
        self.amount = amount

    def __str__(self):   
        return f"forward {self.amount} steps"

    def __repr__(self):
        return f"Move({self.amount})"

    def copy(self):
        return Move(self.amount)

    @property
    def param(self):
        return self.amount

    @param.setter
    def param(self, amount):
        self.amount = amount

class Turn():

    def __init__(self, degrees = 0):
        self.degrees = degrees

    def __str__(self):
        return f"turn {self.degrees} degrees"

    def __repr__(self):
        return f"Turn({self.degrees})"

    def copy(self):
        return Turn(self.degrees)


# Class to parse JSON input file
# The updated config will be consumed by speedUp object
class updateConfig:

    def __init__(self, fp):
        self.fp = fp


# Class to turn speedUp object into JSON
# that will be output
class outputJSON:

    def __init__(self, speedUp, fp):
        self.speedUp = speedUp
        self.fp = fp