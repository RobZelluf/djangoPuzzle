from fill_answers import antwoorden

letters = "abcdefghijklmnopqrstuvwxyz"

count = 0
found = []

for antwoord in antwoorden:
    antwoord_split = [x for x in antwoord.lower()]
    for letter in letters:
        matching = [x for x in antwoord_split if x == letter]
        if len(matching) == 3:
            count += 1
            found.append(antwoord)
            break

print(sorted(found))
print(count)

