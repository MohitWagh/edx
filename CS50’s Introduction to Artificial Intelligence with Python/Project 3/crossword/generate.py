import math
import sys

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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains:
            elements_to_remove = set()
            for x in self.domains[v]:
                if len(x) != v.length:
                    elements_to_remove.add(x)
            self.domains[v] = self.domains[v] - elements_to_remove

    def revise_consistency_given_domains(self, overlap, x_domain, y_domain):
        """
        Find the values in x_domain for which there is no corresponding value in y_domain.

        Return the set of values that do not correspond as a set.
        """
        (x_index, y_index) = overlap
        changes = set()
        for i in x_domain:
            corresponding_val_exists = False
            for j in y_domain:
                if i[x_index] == j[y_index]:
                    corresponding_val_exists = True
                    break
            if not corresponding_val_exists:
                changes.add(i)
        return changes

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[(x, y)]
        if overlap:
            changes = self.revise_consistency_given_domains(overlap, self.domains[x], self.domains[y])
            self.domains[x] = self.domains[x] - changes
            return len(changes) != 0
        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            for v in self.crossword.variables:
                for neighbour in self.crossword.neighbors(v):
                    arcs.append((v, neighbour))
        while arcs:
            to_revise = arcs.pop()
            changes = self.revise(to_revise[0], to_revise[1])
            if len(self.domains[to_revise[0]]) == 0:
                return False
            if changes:
                for neighbour in self.crossword.neighbors(to_revise[0]):
                    arcs.append((neighbour, to_revise[0]))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(self.crossword.variables - assignment.keys()) == 0

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for i in assignment:
            if i.length != len(assignment[i]):
                return False
            for j in assignment:
                if i == j:
                    continue
                if assignment[i] == assignment[j]:
                    return False
                if self.crossword.overlaps[(i, j)] is None:
                    continue
                else:
                    i_index, j_index = self.crossword.overlaps[(i, j)]
                    if assignment[i][i_index] != assignment[j][j_index]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        ruled_out = dict()
        for i in self.domains[var]:
            ruled_out_domains = 0
            for j in self.crossword.neighbors(var):
                if j in assignment.keys():
                    continue
                ruled_out_domains += len(
                    self.revise_consistency_given_domains(self.crossword.overlaps[(j, var)], self.domains[j], {i}))
            if ruled_out_domains in ruled_out.keys():
                ruled_out[ruled_out_domains].append(i)
            else:
                ruled_out[ruled_out_domains] = [i]
        return_list = []
        for x in sorted(ruled_out):
            return_list += ruled_out[x]
        return return_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        if self.assignment_complete(assignment):
            return None
        unassigned = self.crossword.variables - assignment.keys()
        min_values = math.inf
        min_variable = None
        for i in unassigned:
            if len(self.domains[i]) < min_values:
                min_values = len(self.domains[i])
                min_variable = i
        return min_variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        unassigned = self.select_unassigned_variable(assignment)
        if unassigned is None:
            return assignment
        for i in self.order_domain_values(unassigned, assignment):
            assignment[unassigned] = i
            # changed_domain = self.domains[unassigned] - {i}
            self.domains[unassigned].clear()
            self.domains[unassigned].add(i)
            if not self.consistent(assignment) or not self.maintain_ac3(unassigned) or self.backtrack(assignment) is None:
                assignment.pop(unassigned)
                # self.domains[unassigned].update(changed_domain)
            else:
                return assignment
        return None

    def maintain_ac3(self, assigned):
        arcs = []
        for i in self.crossword.neighbors(assigned):
            arcs.append((i, assigned))
        return self.ac3(arcs)


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
