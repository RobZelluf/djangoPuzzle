import os


def get_filename():
    filename = sorted(os.listdir("/home/rob/Documents/puzzleDjango/excel_files/"), key=lambda x: x[:4:-5])[-1]
    filename = "/home/rob/Documents/puzzleDjango/excel_files/" + filename

    return filename