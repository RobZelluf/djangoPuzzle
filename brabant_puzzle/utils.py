import os


def get_filename():
    filenames = os.listdir("/home/rob/Documents/puzzleDjango/excel_files/")

    filename = sorted(os.listdir("/home/rob/Documents/puzzleDjango/excel_files/"))[-1]
    filename = "/home/rob/Documents/puzzleDjango/excel_files/" + filename

    return filename