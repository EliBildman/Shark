from pypokerengine.utils.card_utils import gen_cards, gen_deck, estimate_hole_card_win_rate
from itertools import combinations
import uuid
from copy import copy, deepcopy

N_TESTS = 100
deck = gen_deck().deck

def all_holes():
    return all_combinations(2)

def all_combinations(n, exclude_cards = []):
    _deck = gen_deck(exclude_cards=exclude_cards).deck
    return list(combinations(_deck, n))

class NatureNode(): #need to scale for more than 2 players

    def __init__(self, parent = None, hole = [], comm = [], stage = 'PREFLOP'):
        self.parent = parent
        self.hole = hole
        self.comm = comm
        self.children = []
        self.wr = None
        self.stage = stage
        self.id = uuid.uuid1()

    def get_wr(self):
        if self.wr:
            return self.wr
        return self.mc_estimate_wr(N_TESTS)

    def mc_estimate_wr(self, n_tests):
        self.wr = estimate_hole_card_win_rate(
                    nb_simulation=n_tests,
                    nb_player= 2,
                    hole_card= self.hole,
                    community_card= self.comm
                )
        return self.wr

    def get_children(self):

        if self.children:
            return self.children
        
        if self.stage == 'PREFLOP':
            for h in all_holes():
                self.children.append(NatureNode(parent = self, hole = list(h), stage='FLOP'))

        elif self.stage == 'FLOP':
            for f in all_combinations(n = 3, exclude_cards = self.hole):
                self.children.append(NatureNode(parent = self, hole = self.hole, comm = list(f), stage='TURN'))

        elif self.stage in ['TURN', 'RIVER']:
            for c in all_combinations(n = 1, exclude_cards = self.hole + self.comm):
                self.children.append(NatureNode(parent = self, hole = self.hole, comm = self.comm + list(c), stage= 'RIVER' if self.stage == 'TURN' else 'END'))

        else:
            #do something with endstages idk man
            pass

        return self.children

    def __str__(self):
        # print(self.id)
        tag = str(self.id) + '$' + (str(self.wr) if self.wr else '') + '$'
        for card in self.hole:
            tag += str(card.suit) + ':' + str(card.rank) + ','
        tag += '$'
        for card in self.comm:
            tag += str(card.suit) + ':' + str(card.rank) + ','
        tag += '$'
        for child in self.children:
            tag += str(child.id) + ','
        return tag


class AbstractNatureNode():

    def __init__(self, parent, wr, p = 0, children = []):
        self.parent = parent
        self.wr = wr
        self.children = children.copy()
        self.p = p

    def get_wr(self):
        return self.wr

    def get_children(self):
        return self.children




