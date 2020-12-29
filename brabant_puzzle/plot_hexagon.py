import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from brabant_puzzle.make_puzzle import puzzle, category_cells
import numpy as np
import pandas as pd
import datetime
import json


class Plotter:
    def __init__(self, size=40, template=False):
        self.size = size
        self.template = template

        with open("/home/rob/Documents/puzzleDjango/brabant_puzzle/settings.txt", "r") as f:
            settings = json.load(f)

        if not template:
            self.filepath = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images/latest_solution.png"
        else:
            self.filepath = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images/template.png"

        prefilled_filename = "/home/rob/Documents/puzzleDjango/brabant_puzzle/puzzle_filled.csv"
        with open(prefilled_filename, "r") as f:
            df = pd.read_csv(f)
            self.filled = list(df.Answer)

        if settings["use_self_filled"] == "True":
            selffilled_filename = "/home/rob/Documents/puzzleDjango/brabant_puzzle/self_filled.csv"
            with open(selffilled_filename, "r") as f:
                df = pd.read_csv(f)
                self.self_filled = list(df.Answer)
        else:
            self.self_filled = []

    def plot(self, S, all_options):
        fig, ax = plt.subplots(figsize=(self.size, self.size))
        ax.set_aspect('equal')
        self.fig = fig
        self.ax = ax

        size = 1

        coord = []
        colors = []
        labels = []

        for i, row in enumerate(puzzle):
            for j, cell in enumerate(row):
                if i <= 7:
                    x = -i + j
                    y = -j
                else:
                    x = -7 + j
                    y = -i - j + 7

                z = i

                coord.append([x, y, z])
                if cell in category_cells:
                    colors.append(["White"])
                else:
                    colors.append(["Green"])

                if S[cell] is None:
                    labels.append([""])
                else:
                    labels.append([all_options[S[cell]]])

        # Horizontal cartesian coords
        hcoord = [c[0] * size for c in coord]

        # Vertical cartersian coords
        vcoord = [size * 2. * np.sin(np.radians(60)) * (c[1] - c[2]) /3. for c in coord]

        # Add some coloured hexagons
        for i, (x, y, c, l) in enumerate(zip(hcoord, vcoord, colors, labels)):

            color = c[0].lower()  # matplotlib understands lower case words for colours
            hex = RegularPolygon((x, y), numVertices=6, radius=2. / 3. * size,
                                 orientation=np.radians(30),
                                 facecolor=color, alpha=0.2, edgecolor='k')
            self.ax.add_patch(hex)
            # Also add a text label
            if l[0] in self.filled:
                self.ax.text(x, y, l[0], ha='center', va='center', size=2, fontsize=10, weight='bold')
            elif l[0] in self.self_filled:
                self.ax.text(x, y, l[0], ha='center', va='center', size=2, fontsize=10, weight='light', color="red")
            else:
                self.ax.text(x, y, l[0], ha='center', va='center', size=2, fontsize=10)

            self.ax.text(x, y - 0.2, i, ha='center', va='center', size=2, fontsize=10)

        # Also add scatter points in hexagon centres
        self.ax.scatter(hcoord, vcoord, c=[c[0].lower() for c in colors], alpha=0.0)

        # Plot timestamp
        self.ax.text(-8, 0, datetime.datetime.now().strftime("%H:%M:%S"), size=30, fontsize=30)

        string = "Filled: " + str(len([j for j in S if j is not None]) - len(self.self_filled) - len(self.filled)) + " / " + str(len(S) - len(self.self_filled) - len(self.filled))
        self.ax.text(-8, -0.3, string, size=30, fontsize=30)

        # Show outside categories
        rotations = [30, -30, -90, 30, -30, 90]
        positions = [[-4, -1], [4, -1], [8, -8], [4, -15], [-4, -15], [-8, -8]]
        for i, category in enumerate(self.filled[-6:]):
            self.ax.text(positions[i][0], positions[i][1], category, size=50, fontsize=50, ha='center', va='center', rotation=rotations[i], rotation_mode='anchor', color='red')

        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)

        self.fig.savefig(self.filepath)
        plt.close(self.fig)


if __name__ == "__main__":
    plotter = Plotter(10)
    S = {i: i for i in range(175)}
    all_options = [v for k, v in S.items()]
    plotter.plot(S, all_options)