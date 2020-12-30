import csv
import pandas as pd
import difflib
import copy
import os
from brabant_puzzle.utils import get_filename

filename = get_filename()

with open(filename, "rb") as f:
    antwoorden_df = pd.read_excel(f, "Antwoorden", index_col=0)
    antwoorden_df = antwoorden_df.iloc[:, 1:9]
    antwoorden = list(antwoorden_df.index)

    categorien_df = pd.read_excel(f, "categorieen", index_col=0)
    categorieen = list(categorien_df.Omschrijving)

    opties = copy.copy(antwoorden)
    opties.extend(categorieen)


if __name__ == "__main__":
    # Write csv file
    puzzle_filename = "puzzle.csv"

    with open(puzzle_filename, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["Cell", "Answer"])

        for cell in range(1, 176):
            answer = input("Cell " + str(cell) + ":")
            if len(answer) > 0:
                matches = difflib.get_close_matches(answer, opties)
                if len(matches) > 0:
                    best_match = matches[0]
                    csv_writer.writerow([cell, best_match])