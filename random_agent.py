from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card, attach_hole_card_from_deck
from random import choice, randint

class RandomAgent(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        c = choice(valid_actions)
        if c['action'] == 'raise':
            return c['action'], randint(c['amount']['min'], c['amount']['max'])
        else:
            return c['action'], c['amount']

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


# from pypokerengine.api.game import setup_config, start_poker

# config = setup_config(max_round=10, initial_stack=100, small_blind_amount=5)
# config.register_player(name="p1", algorithm=RandomAgent())
# config.register_player(name="p2", algorithm=RandomAgent())
# game_result = start_poker(config, verbose=1)