from copy import copy, deepcopy
import uuid

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


#contains all nodes included in iset
#also has strategy for this iset
class WRInfoSet():
    
    #hand_wr: float, his: [Action]
    def __init__(self, example_node):
        self.player = example_node.player
        self.hand_wr = example_node.wrs[example_node.player]
        self.his = example_node.get_history()
        self.id = uuid.uuid1()
        self.strat = []
        self.nodes = []

        self._init_strat(example_node)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def get_nodes(self):
        return self.nodes

    def matches_node(self, node):

        if node.wrs[node.player] != self.hand_wr:
            return False

        n_his = node.get_history()
        for i in range(len(self.his)):
            if self.his[i] != n_his[i]:
                return False

    def p_action(self, action):
        for s in self.strat:
            if s[0] == action:
                return s[1]

    def _init_strat(self, example_node):
        children = example_node.get_children()
        for child in children:
            self.strat.append( (child.last_move, 1 / len(children)) )


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

    def __eq__(self, other):
        return self.player == other.player and self.move.name == other.move.name and self.move.amount == other.move.amount