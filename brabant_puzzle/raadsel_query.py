from easygui import fileopenbox
import pandas as pd
from collections import defaultdict
import numpy as np
from pprint import pprint
from brabant_puzzle.fill_answers import filename

categorie_antwoord = defaultdict(list)
antwoord_categorie = defaultdict(list)


with open(filename, "rb") as f:
    antwoorden_df = pd.read_excel(f, "Antwoorden", index_col=0)
    antwoorden_df = antwoorden_df.iloc[:, 1:9]

    categorien_df = pd.read_excel(f, "categorieen", index_col=0)

for antwoord, categorien in antwoorden_df.iterrows():
    # print("Antwoord:", str(antwoord))
    # print("Categorien:", list(categorien))

    for categorie in categorien:
        if not np.isnan(categorie):
            categorie_beschrijving = categorien_df.loc[categorie].Omschrijving

            categorie_antwoord[categorie_beschrijving].append(antwoord)
            antwoord_categorie[antwoord].append(categorie_beschrijving)


if __name__ == "__main__":
    while True:
        cat1 = int(input("Categorie nummer 1:"))
        cat2 = int(input("Categorie nummer 2:"))

        cat1 = categorien_df.loc[cat1].Omschrijving
        cat2 = categorien_df.loc[cat2].Omschrijving

        answers1 = categorie_antwoord[cat1]
        answers2 = categorie_antwoord[cat2]

        match = list(np.intersect1d(answers1, answers2))

        pprint(match)
        while True:
            inp = input("Type a number to add a category, press Enter to start again:")
            if len(inp) == 0:
                break
            else:
                new_cat = int(inp)
                new_cat = categorien_df.loc[new_cat].Omschrijving
                new_answers = categorie_antwoord[new_cat]

                match = list(np.intersect1d(match, new_answers))
                if len(match) == 0:
                    print("No matches found!")
                    break

                pprint(match)


