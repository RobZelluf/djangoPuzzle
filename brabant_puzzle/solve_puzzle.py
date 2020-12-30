from brabant_puzzle.utils import get_all_options
import matplotlib.pyplot as plt
from make_puzzle import category_cells
from fill_answers import categorieen, antwoorden
from make_puzzle import neighs as adjacency_dict
from plot_hexagon import Plotter
from utils import get_filename, get_data
import copy
from queue import PriorityQueue
import pickle as p
import datetime
import random
import numpy as np
from time import time
import json
import os
from functools import reduce

import pandas as pd
from collections import defaultdict


class Solver:
    def __init__(self):
        antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties = get_data()

        self.filename = get_filename()
        print(self.filename)
        self.plotter = Plotter()

        self.cell_visited = []

        self.heatmap = defaultdict(list)
        self.last_plotted = time()

        self.fig = plt.figure(figsize=(14, 5))
        self.last_saved = time()
        self.best_time = ""

        self.all_options = get_all_options()

        with open("settings.txt", "r") as f:
            self.settings = json.load(f)

        # Make big overlap matrix
        self.overlaps = np.zeros((len(self.all_options), len(self.all_options)))

        self.category_ind = []
        self.answers_ind = []

        for i, option in enumerate(self.all_options):
            if option in antwoorden:
                self.answers_ind.append(i)

                neighs = antwoord_categorie[option]
                neighs_ind = [self.all_options.index(x) for x in neighs]
                for x in neighs_ind:
                    self.overlaps[i, x] = 1
                    self.overlaps[x, i] = 1

            elif option in categorieen:
                self.category_ind.append(i)

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
        self.visited = set()
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
        self.found_better_time = time()
        self.found_better_times = []

    def get_settings(self):
        with open("settings.txt", "r") as f:
            settings = json.load(f)

        return settings

    def check_stuck(self, S):
        for cell, value in enumerate(S):
            if value is None:
                all_options = []
                neighs = adjacency_dict[cell]
                for neigh in neighs:
                    all_options.append(self.overlaps[neigh])

                options = reduce(np.intersect1d, all_options)
                # options = [opt for opt in options if opt not in S]
                if len(options) == 0:
                    return True

        return False

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
        cell_options = defaultdict(int)

        neighbors = []

        if self.settings["mode"] == "reverse":
            lst = reversed(list(enumerate(S)))
        else:
            lst = enumerate(S)

        for cell, fill in lst:
            if fill is None:
                if cell in category_cells:
                    for category in self.category_ind:
                        times = [time()]
                        valid, matches = self.verify_insert(S, cell, category)
                        times.append(time())
                        if valid:
                            new_S = copy.copy(S)
                            cell_options[cell] += 1

                            new_S[cell] = category

                            if hash(tuple(new_S)) not in visited and not stop_adding:
                                neighbors.append((category, new_S, matches))

                            options[category] += 1
                else:
                    for antwoord in self.answers_ind:
                        valid, matches = self.verify_insert(S, cell, antwoord)

                        if valid:
                            new_S = copy.copy(S)
                            cell_options[cell] += 1
                            new_S[cell] = antwoord
                            if hash(tuple(new_S)) not in visited and not stop_adding:
                                neighbors.append((antwoord, new_S, matches))

                            options[antwoord] += 1

                if self.settings["mode"] != "random" and not stop_adding:
                    stop_adding = True
                    if "star" not in self.settings["algorithm"]:
                        break

        random.shuffle(neighbors)
        return neighbors, options, cell_options

    def solve(self):
        t0 = time()
        while not self.queue.empty():
            diff = time() - t0
            if diff > 10:
                return

            prio, _, S = copy.deepcopy(self.queue.get())
            self.visited.add(hash(tuple(S)))

            neighs, options, cell_options = self.get_neighbor_states(S, self.visited)
            for added, new_S, matches in neighs:
                # Add values to heatmap
                for cell, value in enumerate(new_S):
                    if value not in self.heatmap[cell] and value is not None:
                        self.heatmap[cell].append(value)

                depth = len([s for s in S if s is not None])
                self.cell_visited.append(depth)
                if len(self.cell_visited) > 1000000:
                    self.cell_visited = self.cell_visited[-1000000:]

                if time() - self.last_saved > depth:
                    DIR = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images"
                    curr_files = [file for file in os.listdir(DIR) if "visited" in file]

                    filename = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images/visited" + str(int(random.uniform(1000, 2000))) + ".png"
                    self.last_saved = time()
                    plt.plot(self.cell_visited, linewidth=0.5)
                    self.fig.tight_layout()

                    plt.savefig(filename)

                    for file in curr_files:
                        if file not in filename:
                            os.remove(os.path.join(DIR, file))

                    self.fig.clf()

                nones = [v for k, v in enumerate(new_S) if v is None]
                num_unfilled = len(nones)
                if num_unfilled < self.least_unfilled:
                    if self.check_stuck(new_S):
                        continue

                    self.found_better_times.append(time() - self.found_better_time)
                    self.found_better_time = time()

                    avg_time = float(np.mean(self.found_better_times))

                    self.best_time = datetime.datetime.now().strftime("%H:%M:%S")

                    now = datetime.datetime.now().strftime("%H:%M:%S")

                    num_filled = len([x for x in new_S if x is not None])

                    print("Found closer solution:", num_unfilled,  ". Filled:", num_filled, "(", now, ") - (", self.queue.qsize(), ")")
                    self.least_unfilled = num_unfilled
                    self.best_solution = copy.deepcopy(new_S)

                    if time() - self.last_plotted > min(len(self.found_better_times), 30):
                        self.last_plotted = time()
                        self.plotter.plot(new_S, self.all_options, self.heatmap, self.best_time, avg_time)

                elif time() - self.last_plotted > 60:
                    self.last_plotted = time()
                    avg_time = float(np.mean(self.found_better_times))
                    self.plotter.plot(self.best_solution, self.all_options, self.heatmap, self.best_time, avg_time)

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

                elif "star" in self.settings["algorithm"]:
                    prio = options[added]

                    if self.settings["algorithm"] in ["c-star", "d-star"]:
                        prio -= matches

                    if self.settings["algorithm"] == "d-star":
                        prio += cell_options[new_S.index(added)]

                    if self.settings["algorithm"] in ["c-star"]:
                        prio += num_unfilled

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


