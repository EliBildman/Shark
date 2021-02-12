from simple_game_state import GameState, ValueState
from pypokerengine.utils.card_utils import gen_cards

MAX_DEPTH = 15

def search_value(state, dir, depth=0):

    if type(state) == ValueState:
        return state.value

    if state.round_ended or depth >= MAX_DEPTH:
        # print(state.get_value().value)
        return state.get_value().value

    # print(state.comm_len)

    moves = state.gen_next_states()
    ext = None
    for m in moves:
        v = search_value(moves[m], 'MIN' if dir == 'MAX' else 'MAX', depth= depth + 1)
        if (ext == None) or (dir == 'MIN' and v < ext) or (dir == 'MAX' and v > ext):
            ext = v

    return ext



hole = gen_cards(['S4', 'DA'])
comm = gen_cards(['S5', 'H8', 'CK'])

s = GameState(hole, comm, 2, [100, 100], pot=[0,5], curr_bet=5)

moves = s.gen_next_states()

for m in moves:
    print(m, search_value(moves[m], 'MIN'))

# print(search_value(s, 'MAX'))

