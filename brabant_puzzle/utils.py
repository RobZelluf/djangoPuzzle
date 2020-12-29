import os


def get_filename():
    filenames = os.listdir("/home/rob/Documents/puzzleDjango/excel_files/")

    filename = sorted(os.listdir("/home/rob/Documents/puzzleDjango/excel_files/"), key=lambda x: x[:3:-4])[-1]
    filename = "/home/rob/Documents/puzzleDjango/excel_files/" + filename

    return filename