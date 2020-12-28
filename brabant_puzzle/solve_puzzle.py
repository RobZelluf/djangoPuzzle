from make_puzzle import category_cells
from fill_answers import categorieen, antwoorden
from make_puzzle import neighs as adjacency_dict
from raadsel_query import categorie_antwoord, antwoord_categorie
from plot_hexagon import Plotter
from utils import get_filename
import copy
from queue import PriorityQueue
import pickle as p
import datetime
import random
import numpy as np
from time import time
from pprint import pprint

import pandas as pd
from collections import defaultdict

filename = get_filename()
plotter = Plotter()

all_options = copy.copy(categorieen)
all_options.extend(antwoorden)

# Make big overlap matrix
overlaps = np.zeros((len(all_options), len(all_options)))

for i, option in enumerate(all_options):
    if option in antwoorden:
        neighs = antwoord_categorie[option]
        neighs_ind = [all_options.index(x) for x in neighs]
        for x in neighs_ind:
            overlaps[i, x] = 1
            overlaps[x, i] = 1

    elif option in categorieen:
        neighs = categorie_antwoord[option]
        neighs_ind = [all_options.index(x) for x in neighs]
        for x in neighs_ind:
            overlaps[i, x] = 1
            overlaps[x, i] = 1
    else:
        print("Error 420")
        exit()

for antwoord1 in antwoorden:
    for antwoord2 in antwoorden:
        ind1 = all_options.index(antwoord1)
        ind2 = all_options.index(antwoord2)
        overlaps[ind1, ind2] = 1
        overlaps[ind2, ind1] = 1

for category1 in categorieen:
    for category2 in categorieen:
        ind1 = all_options.index(category1)
        ind2 = all_options.index(category2)
        overlaps[ind1, ind2] = 1
        overlaps[ind2, ind1] = 1


def hash(S):
    S_string = "".join([str(x) for x in S])
    return S_string


def verify_insert(S, cell, value):
    if value in S:
        return False, False

    matches = 0
    neighs = adjacency_dict[cell]

    for neigh in neighs:
        neigh_val = S[neigh]
        if neigh_val is not None:
            text_vals = [all_options[neigh_val], all_options[value]]
            if "Bieb" in text_vals and "Eten en Drinken(ED)" in text_vals:
                print("Hanlo")
                print(overlaps[value, neigh_val])
                input()

            if overlaps[value, neigh_val] == 0:
                return False, False
            else:
                matches += 1

    return True, matches


def get_neighbor_states(S, visited):

    options = defaultdict(int)

    neighbors = []
    for cell, fill in enumerate(S):
        if fill is None:
            if cell in category_cells:
                for category in [all_options.index(x) for x in categorieen]:
                    valid, matches = verify_insert(S, cell, category)
                    if valid:
                        new_S = copy.copy(S)

                        new_S[cell] = category
                        if new_S not in visited:
                            neighbors.append((category, new_S))

                        options[category] += 1
            else:
                for antwoord in [all_options.index(x) for x in antwoorden]:
                    valid, matches = verify_insert(S, cell, antwoord)
                    if valid:
                        new_S = copy.copy(S)

                        new_S[cell] = antwoord
                        if new_S not in visited:
                            neighbors.append((antwoord, new_S))

                        options[antwoord] += 1

            break

    random.shuffle(neighbors)
    return neighbors, options


def main():
    solutions = []
    visited = []
    filled = []
    start_S = []

    for i in range(175):
        start_S.append(None)

    with open("puzzle_filled.csv", "r") as f:
        df = pd.read_csv(f, index_col=0)
        for cell, answer in df.iterrows():
            answer = answer.Answer
            answer_int = all_options.index(answer)

            start_S[int(cell)] = answer_int
            filled.append(answer_int)

    with open("self_filled.csv", "r") as f:
        df = pd.read_csv(f, index_col=0)
        for cell, answer in df.iterrows():
            answer = answer.Answer
            answer_int = all_options.index(answer)

            start_S[int(cell)] = answer_int
            filled.append(answer_int)

    queue = PriorityQueue()
    queue.put((0, id(start_S), (start_S, 0)))

    best_prio = 300
    biggest_queue_size = 0
    best_solution = None

    t0 = time()

    while not queue.empty():
        prio, _, (S, d) = copy.deepcopy(queue.get())
        visited.append(S)

        neighs, options = get_neighbor_states(S, visited)
        for added, new_S in neighs:
            nones = [v for k, v in enumerate(new_S) if v is None]
            priority = len(nones)
            if priority < best_prio:
                now = datetime.datetime.now().strftime("%H:%M:%S")
                num_filled = 169 - 29 - priority
                print("Found closer solution:", priority,  ". Filled:", num_filled, "(", now, ") - (", queue.qsize(), ")")
                best_prio = priority
                best_solution = copy.deepcopy(new_S)

                text_solution = {}
                for i, val in enumerate(best_solution):
                    if val is None:
                        text_solution[i] = None
                    else:
                        text_solution[i] = all_options[val]

                print(text_solution)
                plotter.plot(new_S, all_options)

            if queue.qsize() % 100000 == 0 and queue.qsize() > biggest_queue_size:
                biggest_queue_size = queue.qsize()
                print("Queue size:", queue.qsize())

            if priority == 0:
                print("Solved!")
                solutions.append(new_S)
                print("Number of solutions:", len(solutions))
                with open("solved.p", "wb") as f:
                    p.dump(solutions, f)

                continue

            queue.put((priority, [id(new_S), d], [new_S, d]))

    print("Partially solved!")
    with open("partially_solved.p", "wb") as f:
        p.dump(best_solution, f)


if __name__ == "__main__":
    main()
