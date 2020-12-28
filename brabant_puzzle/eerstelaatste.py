from fill_answers import antwoorden
from raadsel_query import categorie_antwoord, antwoord_categorie

count = 0
found = []

for antwoord in antwoorden:
    antwoord_split = [x for x in antwoord.lower()]
    if antwoord_split[0] == antwoord_split[-1]:
        count += 1
        found.append(antwoord)

print("Automatisch:")
print(sorted(found))
print(count)

found = categorie_antwoord["Eerste- en Eindletter hetzelfde"]
print(len(found), sorted(found))

