from easygui import fileopenbox
import pandas as pd
from collections import defaultdict
import numpy as np
from pprint import pprint
from brabant_puzzle.fill_answers import filename
from tabulate import tabulate
from brabant_puzzle.utils import get_data


def find_crossmatch(categories):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties = get_data()
    text_categories = [categorien_df.loc[x].Omschrijving for x in categories]

    all_categories = list(categorie_antwoord.keys())
    all_answers = []

    for category in categories:
        omschrijving = categorien_df.loc[category].Omschrijving
        answers = categorie_antwoord[omschrijving]
        all_answers.append(answers)


    all_matching_answers = defaultdict(list)

    for category in all_categories:
        if category in text_categories:
            continue

        for row in all_answers:
            matching_answers = []
            found = True
            for answer in row:
                matching_categories = antwoord_categorie[answer]
                if category in matching_categories:
                    matching_answers.append(answer)

            all_matching_answers[category].append(matching_answers)

    headers = [""]
    for category in text_categories:
        headers.append(category)

    data = [headers]

    for category, matches in all_matching_answers.items():
        if 0 not in [len(x) for x in matches]:
            row = [category]
            for match in matches:
                row.append(match)

            data.append(row)

    return data


if __name__ == "__main__":
    categories = [17, 29, 19, 43]
    data = find_crossmatch(categories)
    print(tabulate(data))





