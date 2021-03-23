from pypokerengine.utils.card_utils import gen_cards, gen_deck, estimate_hole_card_win_rate
from pprint import pprint
from random import randint, choice
from pypokerengine.engine.hand_evaluator import HandEvaluator
import numpy as np
from itertools import combinations
from scipy.cluster.vq import vq, kmeans, whiten

N_TESTS = 100

#creating abstrction tree

deck = gen_deck().deck

def all_holes():
    return all_combinations(2)

def comb_perms(combs): #hack alert

    for a in combs:
        for b in combs:
            if sorted(a, key= lambda card: (card.suit, card.rank)) == sorted(b, key= lambda card: (card.suit, card.rank)):
                print(a[0].suit, a[0].rank)
                combs.remove(b)

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

class AbstractNatureNode():

    def __init__(self, parent, wr, p = 0, children = []):
        self.parent = parent
        self.wr = wr
        self.children = children
        self.p = p

    def get_wr(self):
        return self.wr

    def get_children(self):
        return self.children


def get_preflop_wrs():
    wrs = []
    tree = NatureNode(stage='PREFLOP')
    i = 0
    print('Geting Preflop Wrs')
    for deal in tree.get_children():
        i += 1
        if( int(i / 1326 * 10) - int( (i - 1) / 1326 * 10) > 0 ):
            print(int(i / 1356 * 100), '%')
        wrs.append( deal.get_wr() )
    return wrs


def flop_wrs_given(hole):

    node = NatureNode(hole=hole, stage='FLOP')
    print('Getting Flop Wrs')
    i = 0
    for n in node.get_children():
        i += 1
        if(int(i / 196) == (i / 196)):
            print(i / 196, '%')
        n.get_wr()


def collapse(parent, n):

    wrs = [node.get_wr() for node in parent.get_children()]
    whitened = whiten(wrs)
    means, _error = kmeans(whitened, n)
    
    abstracted = [AbstractNatureNode(parent, m) for m in means]

    for child in parent.get_children():
        a_node = min(abstracted, key= lambda a: abs(child.get_wr() - a.get_wr()) )
        a_node.p += 1
        for g_child in child.get_children():
            a_node.children.append(g_child)

    s = sum( a.p for a in abstracted )
    for a in abstracted:
        a.p /= s
    
    return abstracted


def build_postflop_tree(hole, flop):

    root = NatureNode(hole=hole, comm=flop, stage='TURN')

    print('Bulding tree')

    for turn in root.get_children():
        turn.get_wr()
        for river in turn.get_children():
            river.get_wr()

    print('Collapsing layer 1')

    a = collapse(root, 5)

    print('Collapsing layer 2')

    for node in a:
        node.children = collapse(node, 5)

    # print(len(a))


    

hole = gen_cards(['H2', 'S8'])
flop = gen_cards(['CA', 'S2', 'HJ'])
build_postflop_tree(hole, flop)