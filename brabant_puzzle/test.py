import json

settings = dict(
    mode="normal"
)

with open('brabant_puzzle/settings.txt', 'w') as f:
    json.dump(settings, f)