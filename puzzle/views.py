from django.http import HttpResponse
from .forms import UploadFileForm, ToolForm
from .models import clear_files, UploadFile, UploadCategories
from PIL import Image
from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from brabant_puzzle.raadsel_query import categorie_antwoord, categorien_df, antwoord_categorie
from brabant_puzzle.cross_match import find_crossmatch
import os

from tabulate import tabulate


def index(request):
    pages = ["solution", "categories", "answers", "upload", "tool"]

    response = ""
    for page in pages:
        response += '<li><a href="' + page + '/">' + page + '</a>'

    return HttpResponse(response)


def solution(request):
    image_path = "puzzle/static/puzzle/images/latest_solution.png"
    try:
        with open(image_path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        red = Image.new('RGBA', (1, 1), (255,0,0,0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response


def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist("files")
        if form.is_valid():
            for f in files:
                curr_files = os.listdir("excel_files")
                print(curr_files)
                count = 0
                new_file = "data" + str(count) + '.xlsm'
                while True:
                    new_file = "data" + str(count) + '.xlsm'
                    if new_file not in curr_files:
                        break

                    count += 1

                f.name = new_file

                print("File:", f, "uploaded!")
                file_instance = UploadFile(files=f)
                file_instance.save()
    else:
        form = UploadFileForm()

    context = {
        'form': form
    }

    return render(request, 'puzzle/index.html', context)


def results(request, category_id):
    category = categorien_df.loc[category_id].Omschrijving
    found = sorted(categorie_antwoord[category])

    output = "<b>" + category + "</b><br><br>"
    output += '<br>'.join([q for q in found])

    return HttpResponse(output)


def categories(request):
    categorien = categorien_df

    output = ""
    for i, category in categorien.iterrows():
        output += '<li><a href="' + str(i) + '">' + category.Omschrijving + '</a>'

    return HttpResponse(output)


def answers(request):
    antwoorden = list(antwoord_categorie.keys())

    output = ""
    for antwoord in antwoorden:
        output += '<li><a href="' + antwoord + '">' + antwoord + '</a>'

    return HttpResponse(output)


def answer_results(request, answer):
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