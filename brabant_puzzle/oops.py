from solve_puzzle import overlaps, all_options
from make_puzzle import neighs


ind1 = all_options.index("Eten en Drinken (ED)")
ind2 = all_options.index("Bieb")

print(ind1, ind2)

print(neighs[ind1])
print(overlaps[ind1, ind2], overlaps[ind2, ind1])