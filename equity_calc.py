from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.hand_evaluator import HandEvaluator

def determine_winrate(hole, comm, n_sim = -1):
    pass



hole = gen_cards(['H4', 'D7'])
comm = gen_cards(['D3', 'C5', 'C6', 'HJ', 'SK'])
opponenet = gen_cards(['H2', 'S9'])

print( "{0:b}".format(HandEvaluator.get_hand(hole, comm)) )
