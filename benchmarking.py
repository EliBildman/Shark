from random_agent import RandomAgent
from adversarial_agent import AdversarialAgent
from honest_agent import HonestAgent
from call_agent import CallAgent

from pypokerengine.api.game import setup_config, start_poker

def test_winrate(p1, p2, num_tests, num_rounds = 10, init_stack = 100, small_blind = 5):
    print('Working...')
    games = []
    for i in range(num_tests):
        if int(i / num_tests * 10) - int((i - 1) / num_tests * 10) > 0:
            print(int(i / num_tests * 100), '% completed')
        config = setup_config(max_round=num_rounds, initial_stack=init_stack, small_blind_amount=small_blind)
        config.register_player(name="p1", algorithm=p1())
        config.register_player(name="p2", algorithm=p2())
        game_result = start_poker(config, verbose=0)

        winner = {'stack': None}

        for p in game_result['players']:
            if winner['stack'] is None or (p['stack'] > winner['stack']):
                winner = p
        win_diff = game_result['players'][0]['stack'] - game_result['players'][1]['stack']

        games.append( {"winner": winner['name'], 'diff': win_diff} )

    p1_dubs = len( list(game for game in games if game['winner'] == 'p1') )
    p2_dubs = num_tests - p1_dubs

    avg_diff = sum( game['diff'] for game in games ) / num_tests

    print('Num tests --', num_tests)
    print('Winrates -- p1:', p1_dubs / num_tests * 100, 'p2:', p2_dubs / num_tests * 100)
    print('Avg stack difference --', avg_diff)


if __name__ == '__main__':
    test_winrate(RandomAgent, CallAgent, 10)