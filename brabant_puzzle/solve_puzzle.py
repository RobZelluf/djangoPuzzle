from brabant_puzzle.utils import get_all_options
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
import json

import pandas as pd
from collections import defaultdict


class Solver:
    def __init__(self):
        self.filename = get_filename()
        print(self.filename)
        self.plotter = Plotter()

        self.all_options = get_all_options()

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

        if self.settings["use_self_filled"] == "True":
            with open("self_filled.csv", "r") as f:
                df = pd.read_csv(f, index_col=0)
                for cell, answer in df.iterrows():
                    answer = answer.Answer
                    answer_int = self.all_options.index(answer)

                    start_S[int(cell)] = answer_int
                    self.filled.append(answer_int)

        # Setup for solving
        self.queue = PriorityQueue()
        self.queue.put((0, id(start_S), start_S))

        self.least_unfilled = 300
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

                if self.overlaps[value, neigh_val] == 0:
                    return False, False
                else:
                    matches += 1

        return True, matches

    def get_neighbor_states(self, S, visited):
        stop_adding = False
        options = defaultdict(int)

        neighbors = []

        if self.settings["mode"] == "reverse":
            lst = reversed(list(enumerate(S)))
        else:
            lst = enumerate(S)

        for cell, fill in lst:
            if fill is None:
                if cell in category_cells:
                    for category in [self.all_options.index(x) for x in categorieen]:
                        valid, matches = self.verify_insert(S, cell, category)
                        if valid:
                            new_S = copy.copy(S)

                            new_S[cell] = category
                            if new_S not in visited and not stop_adding:
                                neighbors.append((category, new_S, matches))

                            options[category] += 1
                else:
                    for antwoord in [self.all_options.index(x) for x in antwoorden]:
                        valid, matches = self.verify_insert(S, cell, antwoord)
                        if valid:
                            new_S = copy.copy(S)

                            new_S[cell] = antwoord
                            if new_S not in visited and not stop_adding:
                                neighbors.append((antwoord, new_S, matches))

                            options[antwoord] += 1

                if self.settings["mode"] != "random" and not stop_adding:
                    stop_adding = True
                    if "star" not in self.settings["algorithm"]:
                        break

        # random.shuffle(neighbors)

        return neighbors, options

    def solve(self):
        t0 = time()
        while not self.queue.empty():
            diff = time() - t0
            if diff > 5:
                return

            prio, _, S = copy.deepcopy(self.queue.get())
            self.visited.append(S)

            neighs, options = self.get_neighbor_states(S, self.visited)
            for added, new_S, matches in neighs:
                nones = [v for k, v in enumerate(new_S) if v is None]
                num_unfilled = len(nones)
                if num_unfilled < self.least_unfilled:
                    now = datetime.datetime.now().strftime("%H:%M:%S")

                    num_filled = len([x for x in new_S if x is not None])

                    print("Found closer solution:", num_unfilled,  ". Filled:", num_filled, "(", now, ") - (", self.queue.qsize(), ")")
                    self.least_unfilled = num_unfilled
                    self.best_solution = copy.deepcopy(new_S)
                    self.plotter.plot(new_S, self.all_options)

                if self.queue.qsize() % 100000 == 0 and self.queue.qsize() > self.biggest_queue_size:
                    self.biggest_queue_size = self.queue.qsize()
                    print("Queue size:", self.queue.qsize())

                if num_unfilled == 0:
                    print("Solved!")
                    self.solutions.append(new_S)
                    print("Number of solutions:", len(self.solutions))
                    with open("solved.p", "wb") as f:
                        p.dump(self.solutions, f)

                    continue

                if self.settings["algorithm"] == "dfs":
                    prio = num_unfilled
                elif self.settings["algorithm"] == "bfs":
                    prio = -num_unfilled
                elif self.settings["algorithm"] == "a-star":
                    prio = -matches

                elif self.settings["algorithm"] == "b-star" or self.settings["algorithm"] == "c-star":
                    if matches == 0:
                        prio = options[added]
                    else:
                        prio = options[added] / matches

                    if self.settings["algorithm"] == "c-star":
                        prio = num_unfilled * prio

                self.queue.put((prio, id(new_S), new_S))

        print("Partially solved!")
        with open("partially_solved.p", "wb") as f:
            p.dump(self.best_solution, f)


if __name__ == "__main__":
    while True:
        solver = Solver()
        start_time = time()
        while True:
            solver.solve()

            if solver.filename != get_filename():
                print("Source excel file changed!")
                break

            if solver.settings != solver.get_settings():
                print("Settings changed!")
                break

            with open("restart.txt", "r") as f:
                restart = f.readline()

            if restart == "True":
                print("Manual restarting!")
                with open("restart.txt", "w") as f:
                    f.write("False")

                break

            if float(solver.settings["timeout"]) > 0:
                timeout = float(solver.settings["timeout"])
                if time() - start_time > 60 * timeout:
                    print("Timing out after", timeout, "minutes!")
                    break


