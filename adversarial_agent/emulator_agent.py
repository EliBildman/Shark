from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card, attach_hole_card_from_deck
import operator


from pprint import pprint

NB_SIMULATION = 1




class RecursiveModel(BasePokerPlayer):

    def __init__(self, uuid, game_rules, depth_level):
        self.uuid = uuid
        self.game_rules = game_rules
        self.depth_level = depth_level
    
    def declare_action(self, valid_actions, hole_card, round_state):
        
        best_move = self.find_move_estimates(valid_actions, hole_card, round_state)

        if best_move == 'fold':
            return valid_actions[0]['action'], 0

        elif best_move == 'call':
            return valid_actions[1]['action'], valid_actions[1]['amount']

        elif best_move == 'min_raise':
            return valid_actions[2]['action'], valid_actions[2]['amount']['min']

        elif best_move == 'max_raise':
            return valid_actions[2]['action'], valid_actions[2]['amount']['max']
                

    def find_move_estimates(self, valid_actions, hole_card, round_state):

        e = Emulator()

        e.set_game_rule(player_num=self.game_rules['player_num'], max_round=self.game_rules['max_round'], small_blind_amount=self.game_rules['small_blind_amount'], ante_amount=self.game_rules['ante_amount'])

        # print(round_state)

        for player in round_state['seats']:
            e.register_player(player['uuid'], RecursiveModel(player['uuid'], self.game_rules, self.depth_level + 1))

        end_utils = {'call': 0, 'fold': 0, 'min_raise': 0, 'max_raise': 0}

        for move in valid_actions:

            for _i in range(NB_SIMULATION):

                # print(_i)

                game_state = self._setup_random_state(round_state, hole_card)

                if move['action'] == 'fold':
                    new_state, _actions = e.apply_action(game_state, 'fold')
                    final_state, _actions = e.run_until_round_finish(new_state)
                    end_utils['fold'] += self._evaluate_utility(final_state)

                elif move['action'] == 'call':
                    new_state, _actions = e.apply_action(game_state, 'call', move['amount'])
                    final_state, _actions = e.run_until_round_finish(new_state)
                    end_utils['call'] += self._evaluate_utility(final_state)

                elif move['action'] == 'raise':
                    #min raise
                    new_state, _actions = e.apply_action(game_state, 'raise', move['amount']['min'])
                    final_state, _actions = e.run_until_round_finish(new_state)
                    end_utils['min_raise'] += self._evaluate_utility(final_state)

                    #max raise
                    new_state, _actions = e.apply_action(game_state, 'raise', move['amount']['max'])
                    final_state, _actions = e.run_until_round_finish(new_state)
                    end_utils['max_raise'] += self._evaluate_utility(final_state)

        best_move = max(end_utils.items(), key=operator.itemgetter(1))[0]

        # print(best_move, end_utils[best_move] / NB_SIMULATION)

        return best_move


    def _evaluate_utility(self, finished_state):
        for player in finished_state['table'].seats.players:
            if player.uuid == self.uuid:
                return player.stack


    #generate gamestate with random opponenet card
    def _setup_random_state(self, round_state, my_hole_card):
        game_state = restore_game_state(round_state)
        game_state['table'].deck.shuffle()
        player_uuids = [player_info['uuid'] for player_info in round_state['seats']]
        for uuid in player_uuids:
            if uuid == self.uuid:
                game_state = attach_hole_card(game_state, uuid, gen_cards(my_hole_card))  # attach my holecard
            else:
                game_state = attach_hole_card_from_deck(game_state, uuid)  # attach opponents holecard at random
        return game_state



class AbstractModel(BasePokerPlayer):

    def __init__(self, hole):
        pass
        #





game_rules = {'player_num': 2, 'max_round': 2, 'small_blind_amount': 5, 'ante_amount': 0}

e = Emulator()

# e.set_game_rule(nb_player, final_round, sb_amount, ante)
e.set_game_rule(player_num=game_rules['player_num'], max_round=game_rules['max_round'], small_blind_amount=game_rules['small_blind_amount'], ante_amount=game_rules['ante_amount'])

e.register_player('p1', RecursiveModel('p1', game_rules, 0))
# e.register_player('p2', FishPlayer())

players_info = {
    "p1": { "name": "player1", "stack": 20 },
    "p2": { "name": "player2", "stack": 20 },
}

initial_state = e.generate_initial_game_state(players_info)
game_state, events = e.start_new_round(initial_state)

# new_state, _events = e.apply_action('call', game_state, 10)

# print(game_state)

final_state, _events = e.run_until_round_finish(game_state)

# updated_state, events = e.apply_action(game_state, "fold", 0)
# updated_state, events = e.apply_action(updated_state, "fold", 0)

print(final_state)