from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadFileForm, ToolForm, SettingsForm, UpdateCellForm
from .models import clear_files, UploadFile, UploadCategories, UploadSettings
from django.shortcuts import redirect
import datetime
import pathlib
import random
from PIL import Image
from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from brabant_puzzle.cross_match import find_crossmatch
from brabant_puzzle.utils import get_all_options, get_data
from brabant_puzzle.make_puzzle import category_cells
from brabant_puzzle.plot_hexagon import Plotter
import os
import json
import pandas as pd
import numpy as np
import pickle as p
import csv

from tabulate import tabulate


all_options = get_all_options()


def index(request):
    pages = ["solution", "old_solutions", "finished_solutions", "terminal", "template", "heatmap", "superheatmap", "categories", "answers", "upload", "tool", "settings", "cells", "restart"]

    response = ""
    for page in pages:
        string = " ".join([x.capitalize() for x in page.split("_")])
        response += '<li style="font-size:30px"><a href="' + page + '/">' + string + '</a>'

    context = {
        "title": "Brabantpuzzel",
        "content": response
    }

    return render(request, "puzzle/base.html", context)


def get_solution_image():
    files = os.listdir("puzzle/static/puzzle/images")
    filename = [file for file in files if "latest_solution" in file][0]
    filename = "/static/puzzle/images/" + filename

    return filename


def get_visited_image():
    files = os.listdir("puzzle/static/puzzle/images")
    filename = [file for file in files if "visited" in file][0]
    filename = "/static/puzzle/images/" + filename

    return filename


def solution(request):
    all_options = get_all_options()

    with open('brabant_puzzle/settings.txt', 'r') as f:
        settings = json.load(f)

    with open('brabant_puzzle/latest_state.p', 'rb') as f:
        new_S = p.load(f)

    left = sorted([v for i, v in enumerate(all_options) if i not in new_S])


    out2 = "<b>Unfilled: </b>"
    out = '<ul style="margin: auto; display: inline-block; list-style-type: none;">'
    for word in left:
        out2 += word + ", "
        out += "<li>" + word + "</li>"

    out = out[:-2]

    out += "</ul>"

    context = {
        "func1": get_solution_image,
        "func2": get_visited_image,
        "out": out,
        "out2": out2,
        "settings": [[k, v] for k, v in settings.items()]
    }

    for k, v in settings.items():
        context[k] = v

    return render(request, 'puzzle/solution.html', context)


def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist("files")
        if form.is_valid():
            for f in files:
                curr_files = os.listdir("excel_files")
                print(curr_files)
                count = 0
                while True:
                    new_file = "data" + str(count) + '.xlsm'
                    if new_file not in curr_files:
                        break

                    count += 1

                f.name = new_file

                print("File:", f, "uploaded!")
                file_instance = UploadFile(files=f)
                file_instance.save()

                return redirect("/puzzle/")
    else:
        form = UploadFileForm()

    context = {
        'form': form
    }

    return render(request, 'puzzle/upload.html', context)


def results(request, category_id):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties, antwoorden_fixed = get_data()

    category = categorien_df.loc[category_id].Omschrijving
    found = sorted(categorie_antwoord[category])
    #
    output = ""
    #
    for answer in found:
        # url = reverse(cell, kwargs={'cell_id': str(i)})
        url = reverse(answer_results, kwargs={'answer': answer})
        output += "<li><a href='" + url + "'>" + answer + "</a>"

    context = {
        "title": category,
        "content": output
    }

    return render(request, 'puzzle/base.html', context)


def categories(request):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties, antwoorden_fixed = get_data()

    categorien = [[i, category.Omschrijving] for i, category in categorien_df.iterrows()]
    categorien = sorted(categorien, key = lambda x : x[1])

    output = ""
    for i, category in categorien:
        output += '<li><a href="' + str(i) + '">' + category + '</a>'

    context = {
        "title": "Categories",
        "content": output
    }

    return render(request, 'puzzle/base.html', context)


def answers(request):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties, antwoorden_fixed = get_data()
    antwoorden = sorted(list(antwoord_categorie.keys()))

    output = ""
    for antwoord in antwoorden:
        url = 'https://nl.wikipedia.org/wiki/Special:Search?search=' + antwoord
        output += '<li><a href="' + antwoord + '">' + antwoord + '</a>'
        output += ' - (<a style="font-size: 10px" href="' + url + '">wiki</a>)'

    context = {
        "title": "Answers",
        "content": output
    }

    return render(request, 'puzzle/base.html', context)


def answer_results(request, answer):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties, antwoorden_fixed = get_data()
    categories = sorted(antwoord_categorie[answer])

    with open('brabant_puzzle/puzzle_filled.csv', 'r') as f:
        puzzle_filled = pd.read_csv(f, index_col=0)

    output = "<b>" + answer + "</b><br><br>"
    for category in categories:
        category_id = categorien_df.loc[categorien_df['Omschrijving'] == category].index[0]

        url = reverse(results, kwargs={'category_id': category_id})
        output += "<li><a href='" + url + "'>" + category + "</a>"

        if category in list(puzzle_filled.Answer):
            output += "*"

        output += "</li>"

    context = {
        "title": answer,
        "content": output
    }

    return render(request, 'puzzle/base.html', context)


def tool(request):
    if request.method == "POST":
        form = ToolForm(request.POST, request.FILES)
        # categories = request.FILES.getlist("fields")
        if form.is_valid():
            categories = form.cleaned_data["categories"]
            categories = [int(x) for x in categories.split(",")]
            print("Categories:", categories)
            data = find_crossmatch(categories)

            html = "<table border=1><tr>"
            for val in data[0]:
                html += "<th>" + val + "</th>"

            html += "</tr>"

            for row in data[1:]:
                html += "<tr>"
                html += "<td><b>" + row[0] + "</b></td>"

                for element in row[1:]:
                    html += "<td>" + "<br>".join(element) + "</td>"

                html += "</tr>"

            context = {
                "title": "Super Nice Tool",
                "content": html
            }

            return render(request, 'puzzle/base.html', context)
    else:
        form = ToolForm()

    context = {
        'title': "Super Nice Tool",
        'form': form
    }

    return render(request, 'puzzle/tool.html', context)


def settings(request):
    if request.method == "POST":
        form = SettingsForm(request.POST, request.FILES)
        # categories = request.FILES.getlist("fields")
        if form.is_valid():
            mode = form.cleaned_data["mode"]
            algorithm = form.cleaned_data["algorithm"]
            timeout = form.cleaned_data["timeout"]
            use_self_filled = form.cleaned_data["use_self_filled"]
            double_check = form.cleaned_data["double_check"]
            use_fixed = form.cleaned_data["use_fixed"]

            data = dict(
                mode=mode,
                algorithm=algorithm,
                timeout=timeout,
                use_self_filled=use_self_filled,
                double_check=double_check,
                use_fixed=use_fixed
            )

            with open('brabant_puzzle/settings.txt', 'w') as f:
                json.dump(data, f)

            return redirect("/puzzle/")

    else:
        form = SettingsForm()

    with open('brabant_puzzle/settings.txt', 'r') as f:
        settings = json.load(f)

    context = {
        'form': form,
        'curent_mode': settings["mode"],
        'current_algorithm': settings["algorithm"],
        'current_timeout': settings["timeout"],
        'current_use_self_filled': settings["use_self_filled"],
        'current_double_check': settings["double_check"],
        'current_use_fixed': settings["use_fixed"]
    }

    return render(request, 'puzzle/settings.html', context)


def cell(request, cell_id):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties, antwoorden_fixed = get_data()

    with open("brabant_puzzle/puzzle_filled.csv", "r") as f:
        df = pd.read_csv(f, index_col=0)
        all_prefilled = list(df.Answer)

    if cell_id in df.index:
        return HttpResponse("Cell " + str(cell_id) + " is pre-filled: " + df.loc[cell_id].Answer)

    with open("brabant_puzzle/self_filled.csv", "r") as f:
        df = pd.read_csv(f, index_col=0)

    curr_value = None
    if int(cell_id) in list(df.index):
        curr_value = df.loc[cell_id].Answer

    all_self_filled = list(df.Answer)

    isCategory = False
    if cell_id in category_cells:
        isCategory = True

    if isCategory:
        options = [k for k, v in categorie_antwoord.items() if k not in all_self_filled and k not in all_prefilled]
    else:
        options = [k for k, v in antwoord_categorie.items() if k not in all_self_filled and k not in all_prefilled]

    options = sorted(options)
    if curr_value is not None:
        options.insert(0, "--Remove--")

    if request.method == "POST":
        form = UpdateCellForm(request.POST, request.FILES, options=options, curr_value=curr_value)
        if form.is_valid():
            answer = form.cleaned_data["answer"]
            if answer == "--Remove--":
                if curr_value is not None:
                    df = df.drop(cell_id)

            else:
                df.loc[cell_id] = answer

            df.to_csv("brabant_puzzle/self_filled.csv")
            return redirect("/puzzle/cells")

    else:
        form = UpdateCellForm(options=options, curr_value=curr_value)

    type = "Answer"
    if isCategory:
        type = "Category"

    context = {
        'form': form,
        'cell_id': cell_id,
        'type': type,
        'curr_value': curr_value
    }

    return render(request, 'puzzle/cell.html', context)


def cells(request):
    with open('brabant_puzzle/puzzle_filled.csv', 'r') as f:
        puzzle_filled = pd.read_csv(f, index_col=0)

    with open('brabant_puzzle/self_filled.csv', 'r') as f:
        self_filled = pd.read_csv(f, index_col=0)

    cells = list(i for i, _ in enumerate(all_options))

    output = ""
    for cell in cells:
        if cell in list(puzzle_filled.index):
            output += '<li><b>Cell ' + str(cell) + '</b> - ' + puzzle_filled.loc[cell].Answer + '</li>'
        elif cell in list(self_filled.index):
            output += '<li><a href="' + str(cell) + '">Cell ' + str(cell) + " - " + self_filled.loc[cell].Answer + '</a>'
        else:
            output += '<li><a href="' + str(cell) + '">Cell ' + str(cell) + '</a>'

    context = {
        "title": "Cells",
        "content": output
    }

    return render(request, 'puzzle/base.html', context)


def template(request):
    plotter = Plotter(template=True)

    S = [None for _ in range(len(all_options))]

    with open("brabant_puzzle/puzzle_filled.csv", "r") as f:
        df = pd.read_csv(f, index_col=0)
        for i, row in df.iterrows():
            S[i] = all_options.index(row.Answer)

    with open("brabant_puzzle/self_filled.csv", "r") as f:
        df = pd.read_csv(f, index_col=0)
        for i, row in df.iterrows():
            S[i] = all_options.index(row.Answer)

    plotter.plot(S, all_options)

    image_path = "puzzle/static/puzzle/images/template.png"
    try:
        with open(image_path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        red = Image.new('RGBA', (1, 1), (255,0,0,0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response


def restart(request):
    with open('brabant_puzzle/restart.txt', "w") as f:
        f.write("True")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def old_solutions(request):
    DIR = "puzzle/static/puzzle/images/old_solutions"
    old_images = sorted(os.listdir(DIR), key=lambda x : int(x[:-13]))
    output = ""
    for image in old_images:
        url = os.path.join("/static/puzzle/images/old_solutions", image)
        fname = pathlib.Path(os.path.join(DIR, image))
        mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime).strftime("%D-%H:%M:%S")
        output += '<li><a href="' + url + '">' + image + '</a> (' + mtime + ')'

    context = {
        "title": "Old solutions",
        "content": output
    }

    return render(request, 'puzzle/base.html', context)


def finished_solutions(request):
    old_images = sorted(pathlib.Path("puzzle/static/puzzle/images/finished_solutions/").iterdir(), key=os.path.getmtime, reverse=True)

    output = ""
    for path in old_images:
        url = "/static/puzzle/images/finished_solutions/" + path.name
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%D-%H:%M:%S")
        output += '<li><a href="' + url + '">' + path.name + '</a> (' + mtime + ')'

    context = {
        "title": "Finished Solutions",
        "content": output
    }

    return render(request, 'puzzle/base.html', context)


def terminal(request):
    with open('brabant_puzzle/terminal.txt', "r") as f:
        lines = f.read().split("\n")

    out = ""
    for line in reversed(lines[1:]):
        out += line + "<br>"

    context = {
        "title": "Terminal",
        "content": out
    }

    return render(request, 'puzzle/terminal.html', context)


def heatmap(request):
    filename = sorted(os.listdir("/home/rob/Documents/puzzleDjango/brabant_puzzle/heatmaps"), key=lambda x: int(x[8:-5]))[-1]
    filename = os.path.join('brabant_puzzle/heatmaps', filename)

    with open(filename, 'r') as f:
        heatmap = json.load(f)

    out = "<b>Heatmap</b><br>"
    heatmap = dict(sorted(heatmap.items(), key=lambda item: len(item[1])))

    for k, v in heatmap.items():
        if len(v) == 0:
            continue

        options = sorted(v)
        out += "Cell " + str(k) + ":<ol>"
        for option in options:
            out += "<li>" + option + "</li>"

        out += "</ol>"

    context = {
        "title": "Heatmap",
        "content": out
    }

    return render(request, 'puzzle/base.html', context)


def superheatmap(request):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties, antwoorden_fixed = get_data()

    n_options = len(opties)
    opties = sorted(opties)

    array = np.zeros((175, n_options))

    DIR = 'brabant_puzzle/heatmaps'
    heatmaps = os.listdir("/home/rob/Documents/puzzleDjango/brabant_puzzle/heatmaps")

    out = ""
    for heatmap in heatmaps:
        with open(os.path.join(DIR, heatmap), 'r') as f:
            heatmap = json.load(f)

        heatmap = dict(sorted(heatmap.items(), key=lambda item: len(item[1])))

        for k, v in heatmap.items():
            if len(v) == 0:
                continue

            for option in v:
                array[int(k), opties.index(option)] += 1

    cells_matches = [[i, len(np.where(cell_options > 0)[0]), cell_options.max()] for i, cell_options in enumerate(array)]
    cells_matches = sorted(cells_matches, key=lambda x: (x[1], -x[2]))

    with open('brabant_puzzle/self_filled.csv', 'r') as f:
        self_filled = pd.read_csv(f, index_col=0)

    with open('brabant_puzzle/settings.txt', 'r') as f:
        settings = json.load(f)

    for i, _, _ in cells_matches:
        # if settings["use_self_filled"] == "True":
        #     if i in list(self_filled.index):
        #         continue

        cell_options = array[i]
        options = np.where(cell_options > 0)
        if len(options[0]) > 0:
            url = reverse(cell, kwargs={'cell_id': str(i)})
            out += '<a href="' + url + '">Cell ' + str(i) + '</a></ol>'

            sorted_options = sorted(options[0], key=lambda x : array[i, x], reverse=True)

            for option in sorted_options:
                out += "<li>" + opties[option] + " (" + str(int(array[i, option])) + ")</li>"

            out += "</ol>"

    # out += "<table border=1><tr><th>Cell</th>"
    #
    # for optie in opties:
    #     out += "<th>" + optie + "</th>"
    #
    # out += "</tr>"
    #
    # for i in range(array.shape[0]):
    #     out += "<tr><td><b>" + str(i) + "</b></td>"
    #     for j, optie in enumerate(opties):
    #         out += "<td>" + str(int(array[i, j])) + "</td>"
    #
    #     out += "</tr>"

    context = {
        "title": "Superheatmap",
        "content": out
    }

    return render(request, 'puzzle/base.html', context)


def clear_cells(request):
    with open('brabant_puzzle/self_filled.csv', 'r') as f:
        df = pd.read_csv(f, index_col=0)
        df.to_csv('brabant_puzzle/old_self_filled/' + str(int(random.uniform(1000, 2000))) + ".csv")

    with open('brabant_puzzle/self_filled.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['Cell', 'Answer'])

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
