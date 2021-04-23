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

    #wr: float
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

    #returns if this is the bottom row
    def is_final(self):
        return len(self.conns) == 0

    #get child nodes as list of tuples (WR_Node, p)
    def get_children(self):
        children = []
        for c in self.conns:
            children.append( (c.child, c.p()) )
        return children
        
#combines many (2) WRNodes to represent the full effect of a deal on many (2) players
class WRNatureNode():

    #wr_nodes: [WRNode], children: [WRNatureNode], t: float
    #t is transition prob from last nature state
    def __init__(self, wr_nodes, t):
        self.p1_wr, self.p2_wr = wr_nodes
        self.children = []
        self.t = t


    #get array of (children, p) where p is combined probability of both nature events
    def get_children(self):
        if self.children:
            return self.children

        for p1_c, p1_p in self.p1_wr.get_children():
            for p2_c, p2_p in self.p2_wr.get_children():
                self.children.append( WRNatureNode([p1_c, p2_c], p1_p * p2_p) )

        return self.children

    #is the end of a round
    def is_final(self):
        return self.p1_wr.is_final() and self.p2_wr.is_final() 

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


class DecisionNode():

    def __init__(self, parent, gamestate, raise_amounts, last_action = None, children = [], round_over = False):
        self.parent = parent
        self.gamestate = gamestate
        self.children = children[:]
        self.round_over = round_over
        self.raise_amounts = raise_amounts
        self.last_action = last_action

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

        ends_round = new_state.turn >= new_state.n_players

        act = Action(player, Move('call'))

        return DecisionNode(self, new_state, self.raise_amounts, last_action= act, round_over= ends_round)

    def _get_fold(self):

        v = -self.gamestate.pots[0] if self.gamestate.player() == 0 else self.gamestate.pots[1]
        act = Action(self.gamestate.player(), Move('fold'))
        return ValueNode(v, act)

    def _get_raise(self, raise_amount): #amount taken in bbs
        
        new_state = deepcopy(self.gamestate)
        opp = self.gamestate.opp_player()
        player = self.gamestate.player()

        call_amount = self.gamestate.pots[opp] - self.gamestate.pots[player]

        new_state.pots[player] += call_amount + raise_amount
        new_state.stacks[player] -= call_amount + raise_amount

        new_state.turn += 1

        act = Action(player, Move('riase', amount= raise_amount))

        return DecisionNode(self, new_state, self.raise_amounts, last_action= act)


    def get_children(self):
        
        if self.children:
            return self.children

        if self.round_over:
            return []
            # raise Exception('round over')
        
        self.children.append(self._get_fold())
        self.children.append(self._get_call())

        for r in self.raise_amounts:
            # print(self.gamestate.pots[self.gamestate.player] + r )
            if self.gamestate.pots[self.gamestate.player()] + r <= self.gamestate.max_bet:
                self.children.append(self._get_raise(r))

        return self.children

#the leaf nodes of the decision tree, wiht deterministic value
class ValueNode():

    def __init__(self, value, last_action):
        self.last_action = last_action
        self.value = value

#a move made with name and amount info
class Move():

    def __init__(self, name, amount = None):
        self.name = name
        self.amount = amount

#a move made by a player
class Action():

    #player: int, move: int
    def __init__(self, player, move):
        self.player = player
        self.move = move


class WrInfoSet():
    
    #hand_wr: float, his: [Action]
    def __init__(self, hand_wr, his):
        self.hand_wr = hand_wr
        self.his = his
        self.id = uuid.uuid1()