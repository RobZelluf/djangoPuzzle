import copy
import os
import pandas as pd
from collections import defaultdict
import numpy as np


def get_filename():
    filename = sorted(os.listdir("/home/rob/Documents/puzzleDjango/excel_files/"), key=lambda x: int(x[4:-5]))[-1]
    filename = "/home/rob/Documents/puzzleDjango/excel_files/" + filename

    return filename


def get_data():
    filename = get_filename()

    with open(filename, "rb") as f:
        antwoorden_df = pd.read_excel(f, "Antwoorden", index_col=0)

        fixed_df = antwoorden_df.iloc[:, 11:13]
        antwoorden_df = antwoorden_df.iloc[:, 1:10]

        antwoorden = list(antwoorden_df.index)

        categorien_df = pd.read_excel(f, "categorieen", index_col=0)
        categorieen = list(categorien_df.Omschrijving)

        opties = copy.copy(antwoorden)
        opties.extend(categorieen)

    # Make more data
    categorie_antwoord = defaultdict(list)
    antwoord_categorie = defaultdict(list)

    with open(filename, "rb") as f:
        antwoorden_df = pd.read_excel(f, "Antwoorden", index_col=0)
        antwoorden_df = antwoorden_df.iloc[:, 1:11]

        categorien_df = pd.read_excel(f, "categorieen", index_col=0)

    for antwoord, categorien in antwoorden_df.iterrows():

        for categorie in categorien:
            if not np.isnan(categorie):
                categorie_beschrijving = categorien_df.loc[categorie].Omschrijving

                categorie_antwoord[categorie_beschrijving].append(antwoord)
                antwoord_categorie[antwoord].append(categorie_beschrijving)

    antwoorden_fixed = {}
    for antwoord, fixed_categories in fixed_df.iterrows():
        fixed_categories = [categorien_df.loc[int(x)].Omschrijving for x in fixed_categories if not np.isnan(x)]

        if len(fixed_categories) > 0:
            antwoorden_fixed[antwoord] = fixed_categories

    return antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties, antwoorden_fixed


def get_all_options():
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties, antwoorden_fixed = get_data()
    all_options = copy.copy(categorieen)
    all_options.extend(antwoorden)

    return all_options