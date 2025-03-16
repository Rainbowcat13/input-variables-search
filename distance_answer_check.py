import sys

import Levenshtein


if len(sys.argv) < 3:
    print("Usage: python distance_answer_check.py [path_to_inputs] [path_to_answer]\nOr backwards")
    exit(1)

with open(sys.argv[1], "r") as inp_f:
    with open(sys.argv[2], "r") as ans_f:
        seq1 = inp_f.readlines()[1].strip()
        seq2 = ans_f.readlines()[1].strip()
        print(Levenshtein.distance(seq1, seq2))
