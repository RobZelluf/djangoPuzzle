import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pathlib
from matplotlib import cm
from matplotlib.patches import RegularPolygon
from brabant_puzzle.make_puzzle import puzzle, category_cells
import numpy as np
import pandas as pd
import datetime
import json
import random
import os


class Plotter:
    def __init__(self, size=30, template=False):
        self.size = size
        self.template = template

        with open("/home/rob/Documents/puzzleDjango/brabant_puzzle/settings.txt", "r") as f:
            settings = json.load(f)

        if not template:
            self.filepath = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images/latest_solution.png"
            self.old_solutions_path = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images/old_solutions"
        else:
            self.filepath = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images/template.png"

        prefilled_filename = "/home/rob/Documents/puzzleDjango/brabant_puzzle/puzzle_filled.csv"
        with open(prefilled_filename, "r") as f:
            df = pd.read_csv(f)
            self.filled = list(df.Answer)

        if settings["use_self_filled"] == "True" or template:
            selffilled_filename = "/home/rob/Documents/puzzleDjango/brabant_puzzle/self_filled.csv"
            with open(selffilled_filename, "r") as f:
                df = pd.read_csv(f)
                self.self_filled = list(df.Answer)
        else:
            self.self_filled = []

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

                labels.append([""])

        # Horizontal cartesian coords
        self.hcoord = [c[0] * size for c in coord]

        # Vertical cartersian coords
        self.vcoord = [size * 2. * np.sin(np.radians(60)) * (c[1] - c[2]) / 3. for c in coord]

        # Add some coloured hexagons
        self.labels = []
        self.hexagons = []

        for i, (x, y, c, l) in enumerate(zip(self.hcoord, self.vcoord, colors, labels)):
            if i in category_cells:
                linewidth = 5
            else:
                linewidth = 1

            color = c[0].lower()  # matplotlib understands lower case words for colours
            hex = RegularPolygon((x, y), numVertices=6, radius=2. / 3. * size,
                                 orientation=np.radians(30),
                                 facecolor=color, alpha=0.5, edgecolor='black', linewidth=linewidth)

            self.hexagons.append(hex)

            text = self.ax.text(x, y, l, ha='center', va='center', size=2, fontsize=10)
            self.ax.text(x, y - 0.2, i, ha='center', va='center', size=2, fontsize=10)
            self.labels.append(text)
            self.ax.add_patch(hex)

        # Also add scatter points in hexagon centres
        self.ax.scatter(self.hcoord, self.vcoord, c=[c[0].lower() for c in colors], alpha=0.0)

        # Show outside categories
        rotations = [30, -30, -90, 30, -30, 90]
        positions = [[-4, -1], [4, -1], [8, -8], [4, -15], [-4, -15], [-8, -8]]
        for i, category in enumerate(self.filled[-6:]):
            self.ax.text(positions[i][0], positions[i][1], category, size=50, fontsize=50, ha='center', va='center', rotation=rotations[i], rotation_mode='anchor', color='red', weight='bold')

        self.best_time = self.ax.text(-8, 0.6, datetime.datetime.now().strftime("%H:%M:%S"), size=30, fontsize=30)
        self.last_saved = self.ax.text(-8, 0.3, datetime.datetime.now().strftime("%H:%M:%S"), size=30, fontsize=30)
        self.stats = self.ax.text(-8, 0.0, "", size=30, fontsize=30)
        self.avg_time = self.ax.text(-8, -0.3, "", size=30, fontsize=30)

        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)

    def plot(self, S, all_options, heatmap=None, best_time="", avg_time=-1):
        remove_filenames = []

        if not self.template:
            DIR = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images"
            files = os.listdir(DIR)
            remove_filenames = [f for f in files if "latest_solution" in f]

            self.filepath = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images/latest_solution" + str(int(random.uniform(1000, 2000))) + ".png"

        labels = []
        for c in S:
            if c is None:
                labels.append("")
            else:
                labels.append(all_options[c])

        # Define heatmap range
        norm = None
        cat_norm = None
        heats = []

        if heatmap is not None:
            heats = [len(v) for k, v in heatmap.items()]
            n_colors = max(heats) - min(heats)

            category_heats = [len(v) for k, v in heatmap.items() if k in category_cells]
            n_cat_colors = max(category_heats) - min(category_heats)

            norm = matplotlib.colors.Normalize(vmin=min(heats), vmax=max(heats) * 1.5)
            cat_norm = matplotlib.colors.Normalize(vmin=min(category_heats), vmax=max(category_heats) * 1.5)

        # Add some coloured hexagons
        for i, (x, y, l) in enumerate(zip(self.hcoord, self.vcoord, labels)):

            if heatmap is not None:
                if i in category_cells:
                    cmap =cm.get_cmap("Oranges_r", n_colors)
                    color = cmap(cat_norm(heats[i]))
                else:
                    cmap = cm.get_cmap("Greens_r", n_cat_colors)
                    color = cmap(norm(heats[i]))

            # Also add a text label
            # self.labels[i].set_text(l)
            self.labels[i].set_text(l)
            self.labels[i].set_ha('center')
            self.labels[i].set_x(x)
            self.labels[i].set_y(y)
            self.labels[i].set_size(2)
            self.labels[i].set_fontsize(10)

            if heatmap is not None:
                self.hexagons[i].set_facecolor(color)

            if l in self.filled:
                self.labels[i].set_weight('bold')
                # self.ax.text(x, y, l, ha='center', va='center', size=2, fontsize=10, weight='bold')

            elif l in self.self_filled:
                self.labels[i].set_weight('bold')
                self.labels[i].set_color('red')
                # self.ax.text(x, y, l, ha='center', va='center', size=2, fontsize=10, weight='light', color="red")

        # Plot timestamp
        self.best_time.set_text("Best time: " + best_time)
        self.last_saved.set_text("Last saved time: " + datetime.datetime.now().strftime("%H:%M:%S"))

        string = "Filled: " + str(len([j for j in S if j is not None]) - len(self.self_filled) - len(self.filled)) + " / " + str(len(S) - len(self.self_filled) - len(self.filled))
        self.stats.set_text(string)

        self.avg_time.set_text("Avg improvement time: " + str(round(float(avg_time), 1)) + " seconds.")

        self.fig.tight_layout()
        self.fig.savefig(self.filepath)

        if not self.template:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            filled = len([s for s in S if s is not None])
            filename = os.path.join(self.old_solutions_path, str(filled) + "_solution.png")
            self.fig.savefig(filename)

        plt.close(self.fig)

        for f in remove_filenames:
            os.remove(os.path.join(DIR, f))


if __name__ == "__main__":
    plotter = Plotter(10)
    S = {i: i for i in range(175)}
    all_options = [v for k, v in S.items()]
    plotter.plot(S, all_options)