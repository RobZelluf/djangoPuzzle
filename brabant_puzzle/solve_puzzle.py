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
import json

import pandas as pd
from collections import defaultdict


class Solver:
    def __init__(self):
        self.filename = get_filename()
        print(self.filename)
        self.plotter = Plotter()

        self.all_options = copy.copy(categorieen)
        self.all_options.extend(antwoorden)

        with open("settings.txt", "r") as f:
            self.settings = json.load(f)

        # Make big overlap matrix
        self.overlaps = np.zeros((len(self.all_options), len(self.all_options)))

        for i, option in enumerate(self.all_options):
            if option in antwoorden:
                neighs = antwoord_categorie[option]
                neighs_ind = [self.all_options.index(x) for x in neighs]
                for x in neighs_ind:
                    self.overlaps[i, x] = 1
                    self.overlaps[x, i] = 1

            elif option in categorieen:
                neighs = categorie_antwoord[option]
                neighs_ind = [self.all_options.index(x) for x in neighs]
                for x in neighs_ind:
                    self.overlaps[i, x] = 1
                    self.overlaps[x, i] = 1
            else:
                print("Error 420")
                exit()

        for antwoord1 in antwoorden:
            for antwoord2 in antwoorden:
                ind1 = self.all_options.index(antwoord1)
                ind2 = self.all_options.index(antwoord2)
                self.overlaps[ind1, ind2] = 1
                self.overlaps[ind2, ind1] = 1

        for category1 in categorieen:
            for category2 in categorieen:
                ind1 = self.all_options.index(category1)
                ind2 = self.all_options.index(category2)
                self.overlaps[ind1, ind2] = 1
                self.overlaps[ind2, ind1] = 1
        self.solutions = []
        self.visited = []
        self.filled = []

        start_S = []

        for i in range(175):
            start_S.append(None)

        with open("puzzle_filled.csv", "r") as f:
            df = pd.read_csv(f, index_col=0)
            for cell, answer in df.iterrows():
                answer = answer.Answer
                answer_int = self.all_options.index(answer)

                start_S[int(cell)] = answer_int
                self.filled.append(answer_int)

        with open("self_filled.csv", "r") as f:
            df = pd.read_csv(f, index_col=0)
            for cell, answer in df.iterrows():
                answer = answer.Answer
                answer_int = self.all_options.index(answer)

                start_S[int(cell)] = answer_int
                self.filled.append(answer_int)

        # Setup for solving
        self.queue = PriorityQueue()
        self.queue.put((0, id(start_S), (start_S, 0)))

        self.best_prio = 300
        self.biggest_queue_size = 0
        self.best_solution = None

    def get_settings(self):
        with open("settings.txt", "r") as f:
            settings = json.load(f)

        return settings

    def verify_insert(self, S, cell, value):
        if value in S:
            return False, False

        matches = 0
        neighs = adjacency_dict[cell]

        for neigh in neighs:
            neigh_val = S[neigh]
            if neigh_val is not None:
                text_vals = [self.all_options[neigh_val], self.all_options[value]]

                if self.overlaps[value, neigh_val] == 0:
                    return False, False
                else:
                    matches += 1

        return True, matches

    def get_neighbor_states(self, S, visited):
        options = defaultdict(int)

        neighbors = []

        if self.settings["mode"] == "reverse":
            lst = reversed(list(enumerate(S)))
        else:
            lst = list(enumerate(S))

        for cell, fill in lst:
            if fill is None:
                if cell in category_cells:
                    for category in [self.all_options.index(x) for x in categorieen]:
                        valid, matches = self.verify_insert(S, cell, category)
                        if valid:
                            new_S = copy.copy(S)

                            new_S[cell] = category
                            if new_S not in visited:
                                neighbors.append((category, new_S))

                            options[category] += 1
                else:
                    for antwoord in [self.all_options.index(x) for x in antwoorden]:
                        valid, matches = self.verify_insert(S, cell, antwoord)
                        if valid:
                            new_S = copy.copy(S)

                            new_S[cell] = antwoord
                            if new_S not in visited:
                                neighbors.append((antwoord, new_S))

                            options[antwoord] += 1

                if self.settings["mode"] != "random":
                    break

        random.shuffle(neighbors)
        return neighbors, options

    def solve(self):
        t0 = time()
        while not self.queue.empty():
            diff = time() - t0
            if diff > 5:
                return

            prio, _, (S, d) = copy.deepcopy(self.queue.get())
            self.visited.append(S)

            neighs, options = self.get_neighbor_states(S, self.visited)
            for added, new_S in neighs:
                nones = [v for k, v in enumerate(new_S) if v is None]
                priority = len(nones)
                if priority < self.best_prio:
                    now = datetime.datetime.now().strftime("%H:%M:%S")

                    num_filled = 0
                    for cell, val in enumerate(new_S):
                        if val is None:
                            num_filled = cell - 1
                            break

                    print("Found closer solution:", priority,  ". Filled:", num_filled, "(", now, ") - (", self.queue.qsize(), ")")
                    self.best_prio = priority
                    self.best_solution = copy.deepcopy(new_S)
                    self.plotter.plot(new_S, self.all_options)

                if self.queue.qsize() % 100000 == 0 and self.queue.qsize() > self.biggest_queue_size:
                    self.biggest_queue_size = self.queue.qsize()
                    print("Queue size:", self.queue.qsize())

                if priority == 0:
                    print("Solved!")
                    self.solutions.append(new_S)
                    print("Number of solutions:", len(self.solutions))
                    with open("solved.p", "wb") as f:
                        p.dump(self.solutions, f)

                    continue

                if self.settings["algorithm"] == "dfs":
                    prio = priority
                else:
                    prio = -priority

                self.queue.put((prio, [id(new_S), d], [new_S, d]))

        print("Partially solved!")
        with open("partially_solved.p", "wb") as f:
            p.dump(self.best_solution, f)


if __name__ == "__main__":
    while True:
        solver = Solver()
        while True:
            solver.solve()

            if solver.filename != get_filename():
                print("Source excel file changed!")
                break

            if solver.settings != solver.get_settings():
                print("Settings changed!")
                break
