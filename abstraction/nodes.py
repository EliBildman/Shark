from pypokerengine.utils.card_utils import gen_cards, gen_deck, estimate_hole_card_win_rate
from itertools import combinations
import uuid
from copy import copy, deepcopy

# from pypokerengine.api.em

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

#connector class between wrnodes
class Conn():
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child
        self.n = 0
        self.total = 1

    def p(self):
        return self.n / self.total

    def inc(self):
        self.n += 1
        self.total += 1

    def dec(self):
        self.total += 1

#nodes to be set in map with N_LEVELS levels of width N_NODES, each level being completely connected to proceeding and succeeding levels
class WRNode():

    def __init__(self, wr):
        self.wr = wr
        self.conns = []

    def add_child(self, child):
        c = Conn(self, child)
        self.conns.append(c)

    def adjust_for(self, child):
        for c in self.conns:
            if c.child is child:
                c.inc()
            else:
                c.dec()
        
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

class GameState():

    def __init__(self, n_players, pots, stacks, turn, max_bet):
        self.n_players = n_players
        self.pots = pots
        self.stacks = stacks
        self.turn = turn
        self.max_bet = max_bet

    def player(self):
        return self.turn % self.n_players

    def opp_player(self):
        return (self.turn + 1) % self.n_players
            

class EDecisionNode():

    def __init__(self, parent):
        pass


class DecisionNode():

    def __init__(self, parent, gamestate, raise_amounts, children = [], round_over = False):
        self.gamestate = gamestate
        self.children = children[:]
        self.round_over = round_over
        self.raise_amounts = raise_amounts

    def check_round_over(self):
        if self.gamestate.turn < self.gamestate.n_players:
            return False
        for i in range(len(self.gamestate.pot)):    
            if self.gamestate.pot[i] != self.gamestate.pot[0]:
                return False
        return True


    def _get_call(self):
        
        new_state = deepcopy(self.gamestate)
        opp = self.gamestate.opp_player()
        player = self.gamestate.player()

        call_amount = self.gamestate.pots[opp] - self.gamestate.pots[player]

        new_state.pots[player] += call_amount
        new_state.stacks[player] -= call_amount
        new_state.turn += 1

        # if call_amount != -0.5:
        #     print(call_amount)

        ends_round = new_state.turn >= new_state.n_players
        return DecisionNode(self, new_state, self.raise_amounts, round_over= ends_round)

    def _get_fold(self):
        v = -self.gamestate.pots[0] if self.gamestate.player() == 0 else self.gamestate.pots[1]
        return ValueNode(v)

    def _get_raise(self, raise_amount): #amount taken in bbs
        
        new_state = deepcopy(self.gamestate)
        opp = self.gamestate.opp_player()
        player = self.gamestate.player()

        call_amount = self.gamestate.pots[opp] - self.gamestate.pots[player]

        new_state.pots[player] += call_amount + raise_amount
        new_state.stacks[player] -= call_amount + raise_amount

        new_state.turn += 1
        return DecisionNode(self, new_state, self.raise_amounts)


    def get_children(self):
        
        if self.children:
            return self.children

        if self.round_over:
            raise Exception('round over')
        
        self.children.append(self._get_fold())
        self.children.append(self._get_call())

        for r in self.raise_amounts:
            # print(self.gamestate.pots[self.gamestate.player] + r )
            if self.gamestate.pots[self.gamestate.player()] + r <= self.gamestate.max_bet:
                self.children.append(self._get_raise(r))

        return self.children


class ValueNode():

    def __init__(self, value):
        self.value = value
