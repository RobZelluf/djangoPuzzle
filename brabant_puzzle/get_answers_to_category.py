from raadsel_query import categorie_antwoord, antwoord_categorie, categorien_df
from solve_puzzle import all_options

omschrijving = categorien_df.loc[7].Omschrijving

found = categorie_antwoord[omschrijving]
print(omschrijving, len(found))
print("--------------------------")

for x in found:
    print(x)