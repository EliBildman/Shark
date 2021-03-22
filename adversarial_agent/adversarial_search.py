from simple_game_state import GameState, ValueState
from pypokerengine.utils.card_utils import gen_cards

# from visualiser.visualiser import Visualiser as vs

MAX_DEPTH = 15

nodes_explored = 0

# @vs(ignore_args=["state", 'depth'], show_argument_name=False, node_properties_kwargs={"shape":"record", "color":"#f57542", "style":"filled", "fillcolor":"grey"})
def search_value(state, dir, depth=0, move='Start'):

    global nodes_explored
    nodes_explored += 1

    if type(state) == ValueState:
        return (state.value, 'Endstate')

    if state.round_ended or depth >= MAX_DEPTH:
        # print(state.get_value().value) 
        return (state.get_value().value, 'Hueristic Value')

    moves = state.gen_next_states()
    ext = (None, None)
    for m in moves:
        v = search_value(state=moves[m], dir='MIN' if dir == 'MAX' else 'MAX', depth= depth + 1, move=m)[0]
        if (ext[0] is None) or (dir == 'MIN' and v <= ext[0]) or (dir == 'MAX' and v >= ext[0]):
            ext = (v, m)

    return ext



# hole = gen_cards(['SA', 'DA'])
# comm = gen_cards(['CA', 'HA', 'CK'])

# s = GameState(hole, comm, 2, [100, 100], pot=[0,0], curr_bet=5)

# print(search_value(state=s, dir='MAX'))

# vs.make_animation(delay=0.2)



