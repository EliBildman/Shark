import numpy.random as rand

actions = ['BET', 'PASS']
deck = [0, 1, 2]


class state():

    def __init__(self, hands = [], history = []):
        self.turn = len(history)
        self.hands = hands
        self.is_deal = len(hands) == 0
        self.history = history
        self.player = self.turn % 2
        self.played_move = history[ len(history) - 1 ] if len(history) > 0 else None

    def get_children(self):
        children = []
        if self.is_deal:
            for card_a in deck:
                for card_b in deck:
                    if card_a != card_b:
                        children.append(state( [ card_a, card_b ], self.history ))
        else:
            for action in actions:
                his = self.history + [action]
                children.append(state( self.hands, his )) 

        return children

    def is_terminal(self):

        if len(self.history) > 1:
            if self.history[ len(self.history) - 1 ] == 'PASS':
                return True
            if self.history[ len(self.history) - 1 ] == self.history[ len(self.history) - 2 ]:
                return True
        
        return False

    def get_value(self):

        if not self.is_terminal():
            raise Exception("Not terminal")

        if self.history[ len(self.history) - 1 ] == 'PASS':
            if self.history[ len(self.history) - 2 ] != 'PASS':
                return 1 if self.player == 0 else -1
        
        n_bets = len(list(x for x in self.history if x == 'BET'))

        v = 2 if n_bets == 2 else 1

        return v if self.hands[0] > self.hands[1] else -v

    def get_move(self, move):
        for s in self.get_children():
            if s.played_move == move:
                return s
        raise Exception('couldntfindthatexeception') 


def info_for(player, state):
    return {"history": state.history, "hand": state.hands[player]}

def play_khun_round(p1, p2):

    game = state()

    while not game.is_terminal():

        if game.is_deal:
            game = rand.choice(game.get_children())

        else:

            if game.player == 0:
                move = p1.get_move(info_for(0, game))
            else:
                move = p2.get_move(info_for(1, game))

            game = game.get_move(move)

    print('final value:', game.get_value())

    p1.take_ending(game)
    p2.take_ending(game)
    

class CFRPlayer():

    def get_move(self, info):
        print(self.get_info_set(info))
        return 'BET'

    def take_ending(self, state):
        pass

    def get_info_set(self, info):
        return str(info['hand']) + str(info['history'])


play_khun_round(CFRPlayer(), CFRPlayer())