from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

generic_knowledge = And(Biconditional(AKnight, Not(AKnave)), Biconditional(BKnight, Not(BKnave)),
                        Biconditional(CKnight, Not(CKnave)))

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Implication(AKnight, And(AKnight, AKnave)), Implication(AKnight, Not(And(AKnight, AKnave)))
)

knowledge0.add(generic_knowledge)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
A_says_puzzle1 = And(AKnave, BKnave)

knowledge1 = And(
    Implication(AKnight, A_says_puzzle1), Implication(AKnave, Not(A_says_puzzle1)), Or(BKnave, BKnight)
)

knowledge1.add(generic_knowledge)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
A_says_puzzle2 = Biconditional(AKnave, BKnave)
B_says_puzzle2 = Biconditional(AKnight, BKnave)

knowledge2 = And(
    Implication(AKnight, A_says_puzzle2), Implication(AKnave, Not(A_says_puzzle2)),
    Implication(BKnight, B_says_puzzle2), Implication(BKnave, B_says_puzzle2)
)

knowledge2.add(generic_knowledge)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
A_says_puzzle3 = Or(AKnight, AKnave)
B_says_puzzle3 = And(Implication(A_says_puzzle3, AKnave), CKnave)
C_says_puzzle3 = AKnight

knowledge3 = And(
    Implication(AKnight, A_says_puzzle3), Implication(AKnave, Not(A_says_puzzle3)),
    Implication(BKnight, B_says_puzzle3), Implication(BKnave, Not(B_says_puzzle3)),
    Implication(CKnight, C_says_puzzle3), Implication(CKnave, Not(C_says_puzzle3))
)

knowledge3.add(generic_knowledge)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
