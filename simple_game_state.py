from hand_type_probs import prob_winning
from pypokerengine.utils.card_utils import gen_cards


class GameState(object):

    def __init__(self, hole, known_comm, n_players, stacks, comm_len = None, pot=None, win_prob = None, curr_bet=0, turn=0):
        self.hole = hole
        self.known_comm = known_comm
        self.n_players = n_players
        self.stacks = stacks
        self.comm_len = comm_len if comm_len is not None else len(known_comm)
        self.pot = pot if pot is not None else list(0 for _ in range(n_players))
        self.curr_bet = curr_bet
        self.turn = turn
        self.round_ended = False

        if win_prob == None:
            self.win_prob = prob_winning(self.hole, self.known_comm)
        else:
            self.win_prob = None

        # print(comm_len, self.comm_len)

        if self._check_round_over():
            curr_bet = 0 #eventually do something with comm here
            self.comm_len += 1
            self.turn = 0
            if self.comm_len > 5:
                self.round_ended = True

        self.better = turn % n_players

    def _check_round_over(self):
        if self.turn < self.n_players:
            return False
        for i in range(len(self.pot)):    
            if self.pot[i] != self.pot[0]:
                return False
        return True

    def _get_fold(self):
        if self.better == 0:
            return ValueState(-1 * self.pot[0])
        else:
            return ValueState(self.pot[1])

    def _get_call(self):
        n_pot = self.pot.copy()
        n_pot[self.better] += min(self.curr_bet, self.stacks[self.better])
        n_stacks = self.stacks.copy()
        n_stacks[self.better] -= min(self.curr_bet, self.stacks[self.better])
        return GameState(self.hole, self.known_comm, self.n_players, n_stacks, self.comm_len, n_pot, self.win_prob, self.curr_bet, self.turn + 1)

    def _get_raise(self, n):
        n_pot = self.pot.copy()
        n_pot[self.better] += self.curr_bet + n
        n_stacks = self.stacks.copy()
        n_stacks[self.better] -= self.curr_bet + n
        return GameState(self.hole, self.known_comm, self.n_players, n_stacks, self.comm_len, n_pot, self.win_prob, self.curr_bet + n, self.turn + 1)

    def get_move(self, move):
        pass

    def gen_next_states(self):
        states = {"FOLD": self._get_fold()}

        if self.stacks[self.better] > 0:
            states["CALL"] = self._get_call()

        if self.stacks[self.better] > self.curr_bet:
            states["MIN_RAISE"] = self._get_raise(1)
            states["MAX_RAISE"] = self._get_raise(self.stacks[self.better] - self.curr_bet)
        return states
        


    def get_value(self):
        p_winning = self.win_prob #prob_winning(self.hole, self.known_comm)
        return ValueState(p_winning * min(self.pot[0], self.pot[1]) - (1 - p_winning) * min(self.pot[0], self.pot[1])) 

    def __str__(self):
        return "GAMESTATE -- Pot: " + str(self.pot) + ", Stacks: " + str(self.stacks) + ", CurrBet: " + str(self.curr_bet) + ", Better: " + str(self.better) + " CommLen:" + str(self.comm_len)


class ValueState(object):

    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return "ENDSTATE -- Value: " + str(self.value)


# hole = gen_cards(['S4', 'DA'])
# comm = gen_cards(['S5', 'H8', 'CK'])

# a = GameState(hole, comm, 2, [5, 95], pot=[5, 5], curr_bet=10)

# _next = a.gen_next_states()

# print(_next["CALL"])