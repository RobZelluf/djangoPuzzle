from fill_answers import antwoorden

letters = "0123456789"
getallen = ["een", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen", "tien"]

count = 0
found = []

for antwoord in antwoorden:
    for getal in getallen:
        if getal in antwoord:
            found.append(antwoord)

    # antwoord_split = [s.lower() for s in antwoord if s.lower() in letters]
    # if len(antwoord_split) > 0:
    #     found.append(antwoord)

print(sorted(found))
print(len(found))

