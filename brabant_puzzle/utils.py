import copy
import os

from brabant_puzzle.fill_answers import categorieen, antwoorden


def get_filename():
    filename = sorted(os.listdir("/home/rob/Documents/puzzleDjango/excel_files/"), key=lambda x: int(x[4:-5]))[-1]
    filename = "/home/rob/Documents/puzzleDjango/excel_files/" + filename

    return filename


def get_all_options():
    all_options = copy.copy(categorieen)
    all_options.extend(antwoorden)

    return all_options