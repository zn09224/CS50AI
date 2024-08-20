import sys
from collections import deque
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        
        for v in self.domains:
            temp = self.domains[v].copy()
            for x in self.domains[v]:
                if len(x) != v.length:
                    temp.remove(x)
            self.domains[v] = temp        

    def revise(self, x, y):
        
        revised = False
        overlap = self.crossword.overlaps[x, y]
        
        if not overlap:
            return revised
        else:
            i, j = overlap
        
        temp = self.domains[x].copy()
        for w in self.domains[x]:
            if not self.constraint_satisfied(w, y, i, j):
                temp.remove(w)
                revised = True
        
        self.domains[x] = temp
        return revised
    
    
    def constraint_satisfied(self, w1, y, i, j):
        
        res = False
        for w2 in self.domains[y]:
            if w1[i] == w2[j]:
                res = True
        
        return res

    def ac3(self, arcs=None):
        
        if arcs == None:
            arcs = self.all_arcs()
        
        queue = deque(arcs)
        
        while queue:
            x, y = queue.popleft()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y: queue.append((z, x))
        
        return True
                        
    
    def all_arcs(self):
        
        res = []
        
        for v in self.crossword.variables:
            for n in self.crossword.neighbors(v):
                res.append((v, n))
        
        print(res)
        return res
        

    def assignment_complete(self, assignment):
        
        return len(assignment) == len(self.crossword.variables)
        

    def consistent(self, assignment):
        
        return (self.check_distinctiveness(assignment) and
                self.check_length(assignment) and
                self.check_conflicts(assignment))
        
    
    def check_distinctiveness(self, assignment):
        
        values = list(assignment.values())
        return len(set(values)) == len(values)
    
    
    def check_length(self, assignment):
        
        for v in assignment:
            if v.length != len(assignment[v]):
                return False
        
        return True
    
    
    def check_conflicts(self, assignment):
        
        for v in assignment:
            for n in self.crossword.neighbors(v):
                if n in assignment:
                    i, j = self.crossword.overlaps[v, n]
                    if assignment[v][i] != assignment[n][j]:
                        return False
        
        return True
    

    def order_domain_values(self, var, assignment):
        
        res = []
        
        for val in self.domains[var]:
            n = self.num_choices_eliminated(var, val, assignment)
            res.append([n, val])
        
        res.sort()
        return [v[1] for v in res]
        
    
    def num_choices_eliminated(self, var, val, assignment):
        
        count = 0
        
        for neighbor in self.crossword.neighbors(var):
            if neighbor not in assignment:
                i, j = self.crossword.overlaps[var, neighbor]
                for word in self.domains[neighbor]:
                    if val[i] != word[j]:
                        count += 1

        return count
        
        
    def select_unassigned_variable(self, assignment):
        
        currMinRemainingValues = float('inf')
        currLargestDegree = float('-inf')
        res = None
        
        for var in self.crossword.variables:
            if var not in assignment:
                if len(self.domains[var]) < currMinRemainingValues:
                    currMinRemainingValues = len(self.domains[var])
                    res = var
                elif (len(self.domains[var]) == currMinRemainingValues and 
                        len(self.crossword.neighbors(var)) >= currLargestDegree):
                    currLargestDegree = len(self.crossword.neighbors(var))
                    res = var

        return res
                    

    def backtrack(self, assignment):
        
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        
        for value in self.order_domain_values(var, assignment):
            temp = copy.deepcopy(assignment)
            temp[var] = value
            if self.consistent(temp):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result:
                    return result
            assignment.pop(var)
        
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
