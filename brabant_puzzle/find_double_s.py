from fill_answers import antwoorden

found = []
for antwoord in antwoorden:
    if "ie" in antwoord.lower():
        found.append(antwoord)

print(len(found), found)