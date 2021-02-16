from csv import reader

odds = []

with open('opening_odds.csv') as f:
    r = reader(f)
    i = -1
    for row in r:
        odds.append([])
        i += 1
        for n in row:
            odds[i].append(n)


print(odds)