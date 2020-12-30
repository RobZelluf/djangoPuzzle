from django.http import HttpResponse
from .forms import UploadFileForm, ToolForm, SettingsForm, UpdateCellForm
from .models import clear_files, UploadFile, UploadCategories, UploadSettings
from django.shortcuts import redirect
import datetime
import pathlib
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

from tabulate import tabulate


all_options = get_all_options()


def index(request):
    pages = ["solution", "old_solutions", "template", "categories", "answers", "upload", "tool", "settings", "cells", "restart"]

    response = ""
    for page in pages:
        response += '<li style="font-size:30px"><a href="' + page + '/">' + page + '</a>'

    return HttpResponse(response)


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
    with open('brabant_puzzle/settings.txt', 'r') as f:
        settings = json.load(f)

    context = {
        "func1": get_solution_image,
        "func2": get_visited_image,
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
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties = get_data()

    category = categorien_df.loc[category_id].Omschrijving
    found = sorted(categorie_antwoord[category])

    output = "<b>" + category + "</b><br><br>"
    output += '<br>'.join([q for q in found])

    return HttpResponse(output)


def categories(request):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties = get_data()

    categorien = [[i, category.Omschrijving] for i, category in categorien_df.iterrows()]
    categorien = sorted(categorien, key = lambda x : x[1])

    output = ""
    for i, category in categorien:
        output += '<li><a href="' + str(i) + '">' + category + '</a>'

    return HttpResponse(output)


def answers(request):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties = get_data()
    antwoorden = sorted(list(antwoord_categorie.keys()))

    output = ""
    for antwoord in antwoorden:
        output += '<li><a href="' + antwoord + '">' + antwoord + '</a>'

    return HttpResponse(output)


def answer_results(request, answer):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties = get_data()
    categories = sorted(antwoord_categorie[answer])

    output = "<b>" + answer + "</b><br><br>"
    output += '<br>'.join([q for q in categories])

    return HttpResponse(output)


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

            return HttpResponse(html)
    else:
        form = ToolForm()

    context = {
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

            data = dict(
                mode=mode,
                algorithm=algorithm,
                timeout=timeout,
                use_self_filled=use_self_filled
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
        'current_use_self_filled': settings["use_self_filled"]
    }

    return render(request, 'puzzle/settings.html', context)


def cell(request, cell_id):
    antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties = get_data()

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
    options.insert(0, "--Remove--")

    if request.method == "POST":
        form = UpdateCellForm(request.POST, request.FILES, options=options, curr_value=curr_value)
        if form.is_valid():
            answer = form.cleaned_data["answer"]
            if answer == "--Remove--" and curr_value is not None:
                df = df.drop(cell_id)

            else:
                df.loc[cell_id] = answer

            df.to_csv("brabant_puzzle/self_filled.csv")
            return redirect("/puzzle/template")

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
    cells = list(i for i, _ in enumerate(all_options))

    output = ""
    for cell in cells:
        output += '<li><a href="' + str(cell) + '">Cell ' + str(cell) + '</a>'

    return HttpResponse(output)


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

    return HttpResponse("Restarted solver!")


def old_solutions(request):
    DIR = "puzzle/static/puzzle/images/old_solutions"
    old_images = sorted(os.listdir(DIR), key=lambda x : int(x[:-13]))
    output = ""
    for image in old_images:
        url = os.path.join("/static/puzzle/images/old_solutions", image)
        fname = pathlib.Path(os.path.join(DIR, image))
        mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime).strftime("%D:%H:%M:%S")
        output += '<li><a href="' + url + '">' + image + '</a> (' + mtime + ')'

    return HttpResponse(output)