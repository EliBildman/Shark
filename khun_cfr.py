import numpy.random as rand
from visualiser.visualiser import Visualiser as vs
from pprint import pprint

actions = ['BET', 'PASS']
deck = [0, 1, 2]

def all_hands():
    hs = []
    for card_a in deck:
        for card_b in deck:
            if card_a != card_b:
                hs.append([card_a, card_b])
    return hs
class state():

    def __init__(self, hands = [], history = []):
        self.turn = len(history)
        self.hands = hands
        self.is_deal = len(hands) == 0
        self.history = history
        self.player = self.turn % 2
        self.played_move = history[ -1 ] if len(history) > 0 else None
        self.children = []

    def get_children(self):

        if len( self.children ) > 0:
            return self.children

        if self.is_deal:
            for hand in all_hands():
                his = self.history
                self.children.append(state( hand, his ))
                        
        else:
            for action in actions:
                his = self.history + [action]
                self.children.append(state( self.hands, his )) 

        return self.children

    def is_terminal(self):

        if len(self.history) > 1:
            if self.history[ -1 ] == 'PASS':
                return True
            if self.history[ -1 ] == self.history[ -2 ]:
                return True
        
        return False

    def get_value(self):

        if not self.is_terminal():
            raise Exception("Not terminal")

        if self.history[ -1 ] == 'PASS':
            if self.history[ -2 ] != 'PASS':
                return 1 if self.player == 0 else -1
        
        n_bets = len(list(x for x in self.history if x == 'BET'))

        v = 2 if n_bets == 2 else 1

        return v if self.hands[0] > self.hands[1] else -v

    def get_move(self, move):
        for s in self.get_children():
            if s.played_move == move:
                return s
        raise Exception('couldntfindthatexeception: ' + move) 

    def __str__(self):
        return 'STATE -> hands: ' + str(self.hands) + ' his: ' + str(self.history) + ' player: ' + str(self.player)


#------------------------------------------------------------------------------

game_tree = state()


def play_khun_round(p1, p2):

    game = state()

    while not game.is_terminal():

        if game.is_deal:
            game = rand.choice(game.get_children())

        else:

            if game.player == 0:
                move = p1.get_move(info_for(0, game))
                print('Player 1 plays:', move)
            else:
                move = p2.get_move(info_for(1, game))
                print('Player 2 plays:', move)

            game = game.get_move(move)

    print('final value:', game.get_value())

    p1.take_ending(game)
    p2.take_ending(game)

#--------------------------------------------------------------------

regret_sums= [
    {},
    {}
]

strat_profile = [
    {},
    {}
]

default_strat = {'PASS': 0.5, 'BET': 0.5}

def info_for(player, state):
    return {"history": state.history, "hand": state.hands[player]}

def get_info_set_by_state(player, state):
        info = info_for(player, state)
        return str(info['hand']) + str(info['history'])

def get_info_set_by_his(player, his, hand):
    return str(hand) + str(his)

def get_state_by_hands(hand):
    for s in game_tree.get_children():
        if s.hands == hand:
            return s
    raise Exception('couldnt find that one: ' + str(hand))

def get_state_by_history(his, hands):
    s = get_state_by_hands(hands)
    for move in his:
        s = s.get_move(move)
    return s

def subbed_strategy(player, infoset, move):

    p_profile = {}
    for iset in strat_profile[player]:
        p_profile[iset] = strat_profile[player][iset].copy()

    if infoset not in p_profile:
        p_profile[infoset] = default_strat.copy()

    for m in p_profile[infoset]:
        if m == move:
            p_profile[infoset][m] = 1
        else: 
            p_profile[infoset][m] = 0

    return p_profile


def prob_for_move(state, player, move, profile):

    infoset = get_info_set_by_state(player, state)
    
    if infoset not in profile:
        profile[infoset] = default_strat.copy()
    
    return profile[infoset][move]
    

#-------------------------------------------------------------
class CFRPlayer():

    def __init__(self, player_num):
        self.num = player_num

    def get_move(self, info):

        infoset = get_info_set_by_state(info, self.num)
        dist = strat_profile[self.num][infoset]
        return rand.choice( list(dist.keys()), list(dist.values()) )

    def take_ending(self, state):
        pass

    def history_prob(self, hands, his, ignore_self = False, sub_strat = None):

        profile = strat_profile[self.num] if sub_strat is None else subbed_strategy(self.num, sub_strat[0], sub_strat[1])

        p = 1/6
        s = get_state_by_hands(hands)
        for i in range(len(his)):

            if i % 2 != self.num or not ignore_self:
                p *= prob_for_move(s, s.player, his[i], profile)
            s = s.get_move(his[i])

        return p

    def cf_value(self, hands, his, sub_strat = None):
        
        possible_terms = []
        his_state = get_state_by_history(his, hands)

        def get_terms(s):
            if s.is_terminal():
                possible_terms.append((s.history, s.get_value()))
            else:
                for child in s.get_children():
                    get_terms(child)

        get_terms(his_state)

        s = 0

        cf_reach_prob = self.history_prob(hands, his, ignore_self=True, sub_strat=sub_strat)
        reach_prob = self.history_prob(hands, his, ignore_self=False, sub_strat=sub_strat)

        for term in possible_terms:
            term_prob = self.history_prob(hands, term[0], ignore_self=False, sub_strat=sub_strat)
            if term_prob != 0:
                end_reach_prob = term_prob / reach_prob #not sure about this, written pi^sigma(h, z) look into further
            else:
                end_reach_prob = 0
            util = term[1] * (-1 if self.num == 1 else 1)
            s += cf_reach_prob * end_reach_prob * util

        return s

    def cf_regret(self, hands, his, action):
        
        his_state = get_state_by_history(his, hands)
        sub_strat = (get_info_set_by_state(self.num, his_state), action)

        return self.cf_value(hands, his, sub_strat = sub_strat) - self.cf_value(hands, his, sub_strat = None)

    def cfr_iset(self, hand, his, action):

        hands = [0, 0]
        hands[self.num] = hand
        
        s = 0
        for opp_hand in deck:
            if opp_hand != hand:
                hands[abs(self.num - 1)] = opp_hand
                s += self.cf_regret(hands, his, action)

        
        return s


    def calc_strat(self, hand, his):

        info_set = get_info_set_by_his(self.num, his, hand) 

        if info_set not in regret_sums[self.num]:
            regret_sums[self.num][info_set] = {}

        s = 0

        for action in actions:
            
            if action not in regret_sums[self.num][info_set]:
                regret_sums[self.num][info_set][action] = 0
            
            cfr = self.cfr_iset(hand, his, action)

            if cfr > 0:
                regret_sums[self.num][info_set][action] += cfr
            
            s += regret_sums[self.num][info_set][action]
        
        strat = {}

        for a in actions:
            if s > 0:
                strat[a] = regret_sums[self.num][info_set][a] / s
            else:
                strat[a] = 1 / len(actions)

        return strat


#-----------------------------------------------------------------------------------------


def train(n):
    
    p1 = CFRPlayer(0)
    p2 = CFRPlayer(1)

    def train_tree(s, player):

        # print(s)

        # print(player.num)

        if s.is_terminal():
            return

        if not s.is_deal and s.player == player.num:

            info = info_for(player.num, s)
            info_set = get_info_set_by_his(player.num, info['history'], info['hand'])
            strat = player.calc_strat(info['hand'], info['history'])
            strat_profile[player.num][info_set] = strat

        for c in s.get_children():
                train_tree(c, player)

    for i in range(n):
        if i % 2 == 0:
            train_tree(game_tree, p1)
        else:
            train_tree(game_tree, p2)

    

train(100)
print('p1')
pprint(regret_sums[0])
print('p2')
pprint(regret_sums[1])

# p1 = CFRPlayer(0)
# p2 = CFRPlayer(1)

# print(p1.cf_regret([1, 0], ['PASS', 'BET'], 'BET'))
# print(strat_profile)
# print(p1.cf_regret([1, 0], ['PASS', 'BET'], 'BET'))