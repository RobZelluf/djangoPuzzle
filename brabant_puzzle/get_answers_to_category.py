from brabant_puzzle.utils import get_data

antwoorden_df, categorien_df, categorie_antwoord, antwoord_categorie, antwoorden, categorieen, opties = get_data()

omschrijving = categorien_df.loc[31].Omschrijving

found = categorie_antwoord[omschrijving]
print(omschrijving, len(found))
print("--------------------------")

for x in found:
    print(x)