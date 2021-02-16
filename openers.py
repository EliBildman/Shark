from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.card import Card
from csv import reader

ranks, suits = Card.RANK_MAP, Card.SUIT_MAP

odds = []

with open('opening_odds.csv') as f:
    r = reader(f)
    i = -1
    for row in r:
        odds.append([])
        i += 1
        for n in row:
            odds[i].append(n)

def get_ind(card):
    global odds
    return odds[0].index( ranks[card.rank] )

def get_odds(hole):
    global odds
    on_suit = (hole[0].suit == hole[1].suit)
    if (hole[0].rank > hole[1].rank) != on_suit:
        return float(odds[ get_ind(hole[1]) ][ get_ind(hole[0]) ])
    else:
        return float(odds[ get_ind(hole[0]) ][ get_ind(hole[1]) ])

x = gen_cards(['SQ', 'SJ'])

print(get_odds(x))

