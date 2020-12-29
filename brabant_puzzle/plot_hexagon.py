import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from make_puzzle import puzzle, category_cells
import numpy as np
import pandas as pd


class Plotter:
    def __init__(self, size=40):
        self.size = size
        self.filepath = "/home/rob/Documents/puzzleDjango/puzzle/static/puzzle/images/latest_solution.png"

        prefilled_filename = 'puzzle_filled.csv'
        with open(prefilled_filename, "r") as f:
            df = pd.read_csv(f)
            self.filled = list(df.Answer)

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

        # coord = [[0,0,0],[0,1,-1],[-1,1,0],[-1,0,1],[0,-1,1],[1,-1,0],[1,0,-1]]
        # colors = [["Green"],["Blue"],["Green"],["Green"],["Red"],["Green"],["Green"]]
        # labels = [['yes'],['no'],['yes'],['no'],['yes'],['no'],['no']]

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
            else:
                self.ax.text(x, y, l[0], ha='center', va='center', size=2, fontsize=10)

            self.ax.text(x, y - 0.2, i, ha='center', va='center', size=2, fontsize=10)

        # Also add scatter points in hexagon centres
        self.ax.scatter(hcoord, vcoord, c=[c[0].lower() for c in colors], alpha=0.0)

        self.fig.savefig(self.filepath)
        plt.close(self.fig)


if __name__ == "__main__":
    plotter = Plotter(10)
    S = {i: i for i in range(175)}
    all_options = [v for k, v in S.items()]
    plotter.plot(S, all_options)