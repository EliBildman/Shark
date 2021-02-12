from simple_game_state import GameState, ValueState
from pypokerengine.utils.card_utils import gen_cards


def search_value(state, dir):

    if type(state) == ValueState:
        return state.value

    if state.round_ended:
        return state.get_value().value

    moves = state.gen_next_states()
    ext = None
    for m in moves:
        v = search_value(moves[m], 'MIN' if dir == 'MAX' else 'MAX')
        if (ext == None) or (dir == 'MIN' and v < ext) or (dir == 'MAX' and v > ext):
            ext = v

    return ext



hole = gen_cards(['S4', 'DA'])
comm = gen_cards(['S5', 'H8', 'CK'])

s = GameState(hole, comm, 2, [100, 100], pot=[0,5], curr_bet=5)

print(search_value(s, 'MAX'))

