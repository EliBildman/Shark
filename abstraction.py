from pypokerengine.utils.card_utils import gen_cards, gen_deck, estimate_hole_card_win_rate
from pprint import pprint
from random import randint, choice
from pypokerengine.engine.hand_evaluator import HandEvaluator

#creating abstrction tree

deck = gen_deck().deck

def all_holes():
    return all_combinations(2)

def all_combinations(n, exclude_cards = []):
    
    combs = []

    if n == 0:
        return combs

    if n == 1:
        return [[c] for c in gen_deck(exclude_cards=exclude_cards).deck]
    
    for comb in all_combinations(n - 1, exclude_cards):
        for card in gen_deck(exclude_cards= comb + exclude_cards ).deck:
            combs.append(comb + [card])

    return combs


class NatureNode(): #need to scale

    def __init__(self, parent = None, hole = [], opp_hole = [], comm = []):
        self.parent = parent
        self.hole = hole
        self.opp_hole = opp_hole
        self.comm = comm
        self.children = []

    def mc_estimate_wr(self, n_tests):
        return estimate_hole_card_win_rate(
                    nb_simulation=n_tests,
                    nb_player= 2,
                    hole_card= self.hole,
                    community_card= self.comm
                )

    def get_children(self, stage):

        if self.children:
            return self.children
        
        if stage == 'DEAL_SELF':
            for h in all_holes():
                self.children.append(NatureNode(parent = self, hole = h))

        elif stage == 'DEAL_OPP':
            for h in all_combinations(n = 2, exclude_cards= self.hole):
                self.children.append(NatureNode(parent = self, hole = self.hole, opp_hole = h))

        elif stage == 'FLOP':
            for f in all_combinations(n = 3, exclude_cards = self.hole + self.opp_hole):
                self.children.append(NatureNode(parent = self, hole = self.hole, opp_hole = self.opp_hole, comm = f))

        elif stage in ['TURN', 'RIVER']:
            for c in all_combinations(n = 1, exclude_cards = self.hole + self.opp_hole + self.comm):
                self.children.append(NatureNode(parent = self, hole = self.hole, opp_hole = self.opp_hole, comm = self.comm + c ))

        return self.children



def build_game_tree():
    
    tree = NatureNode()

    i = 0
    h = tree.get_children("DEAL_SELF")
    print(len(h))
    # for my_deal in tree.get_children("DEAL_SELF"):
    #     print(i / 1326)
    #     i += 1
    #     my_deal.mc_estimate_wr(1000)
                        


def build_info_tree():
    pass

def build_abstract_tree():
    pass


build_game_tree()