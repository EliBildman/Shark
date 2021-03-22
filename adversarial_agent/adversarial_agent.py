from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card, attach_hole_card_from_deck
from pypokerengine.utils.card_utils import gen_cards

from random_agent import RandomAgent
from adversarial_search import search_value
from simple_game_state import GameState
from openers import get_odds


class AdversarialAgent(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        hole = gen_cards(hole_card)
        # print(len(round_state['community_card']))
        if len(round_state['community_card']) > 0:
            comm = gen_cards(round_state['community_card'])
            s = GameState(hole, comm, 2, list(seat['stack'] for seat in round_state['seats']))
            best_move = search_value(s, 'MAX')
            # print(best_move)
            return self._translate_action(valid_actions, best_move[1])
        else:
            dub_odds = get_odds(hole)
            if dub_odds > 0.5:
                return self._get_action(valid_actions, 'call')
            else:
                return self._get_action(valid_actions, 'fold')
    
    def _translate_action(self, valid_actions, act):
        if act == 'FOLD':
            return self._get_action(valid_actions, 'fold')
        elif act == 'CALL':
            return self._get_action(valid_actions, 'call')
        elif act == 'MIN_RAISE':
            return self._get_action(valid_actions, 'raise', 'min')
        elif act == 'MID_RAISE':
            return self._get_action(valid_actions, 'raise', 'mid')
        elif act == 'MAX_RAISE':
            return self._get_action(valid_actions, 'raise', 'max')
        else:
            print("INVALID ACTION:", act)

    def _get_action(self, valid_actions, act, level = None):
        a_list = list(filter(lambda a: a['action'] == act, valid_actions))

        if len(a_list) == 0:
            print('INVALID ACTION:', act)
        a = a_list[0]

        if level is None:
            return a['action'], a['amount']
        else:
            if level == 'min':
                return a['action'], a['amount']['min']
            elif level == 'mid':
                return a['action'], (a['amount']['min'] + a['amount']['max']) / 2
            elif level == 'max':
                return a['action'], a['amount']['max']


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


if __name__ == '__main__':
    config = setup_config(max_round=10, initial_stack=100, small_blind_amount=5)
    config.register_player(name="p1", algorithm=AdversarialAgent())
    config.register_player(name="p2", algorithm=RandomAgent())
    game_result = start_poker(config, verbose=0)
    print(game_result)