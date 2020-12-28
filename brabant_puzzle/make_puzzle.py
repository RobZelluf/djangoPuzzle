import numpy as np
from pprint import pprint
import networkx as nx
import matplotlib.pyplot as plt

elements = [8, 9, 10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 9, 8]
category_cells = [171, 172, 173, 174, 175]

counter = 0

puzzle = []

for n_elements in elements:
    row = []
    for i in range(n_elements):
        row.append(counter)
        counter += 1

    puzzle.append(row)

neighs = dict()

for i, row in enumerate(puzzle):
    for j, cell in enumerate(row):
        # Check if cell is category
        if (i + 1) % 2 == 0 and (j + 1) % 2 == 0:
            category_cells.append(cell)

        cell_neighs = []

        # Get left en right
        if j > 0:
            cell_neighs.append(row[j - 1])

        if j < len(row) - 1:
            cell_neighs.append(row[j + 1])

        # Get neighbors from above
        if i > 0:
            above_row = puzzle[i - 1]
            above_indices = []
            # Check if the row above has less cells than the current row
            if len(row) > len(above_row):
                if j > 0:
                    above_indices.append(j - 1)
                if j < len(above_row):
                    above_indices.append(j)

            # Else, we're in the bottom part of the raster
            else:
                above_indices.extend([j, j + 1])

            for above_index in above_indices:
                cell_neighs.append(above_row[above_index])

        neighs[cell] = cell_neighs

for cell, neigh_cells in neighs.items():
    for neigh_cell in neigh_cells:
        neigh_neighs = neighs[neigh_cell]
        if cell not in neigh_neighs:
            neighs[neigh_cell].append(cell)


neighs[169] = [1, 9, 18, 28, 39, 51, 64, 78]
neighs[170] = [1, 2, 3, 4, 5, 6, 7, 8]
neighs[171] = [8, 17, 27, 38, 50, 63, 77, 92]
neighs[172] = [92, 106, 119, 131, 142, 152, 161, 169]
neighs[173] = [162, 163, 164, 165, 166, 167, 168, 169]
neighs[174] = [78, 93, 107, 120, 132, 143, 153, 162]

for i in range(169, 175):
    neighs[i] = [x - 1 for x in neighs[i]]
    for neigh in neighs[i]:
        neighs[neigh].append(i)


G = nx.Graph()

for cell in neighs.keys():
    G.add_node(cell)

for cell, neigh_cells in neighs.items():
    for neigh in neigh_cells:
        G.add_edge(cell, neigh)





