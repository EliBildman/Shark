from nodes import DecisionNode, ValueNode, GameState

RAISE_AMOUNTS = [0.5, 1, 2, 5]
PLAYERS = 2
BLINDS = [0.5, 1]
MAX_BET = 6

def build_decision_tree():

    init_state = GameState(PLAYERS, BLINDS, [0, 0], 0, MAX_BET)
    root = DecisionNode(None, init_state, RAISE_AMOUNTS)

    def build_children(node):
        for n in node.get_children():
            if type(n) != ValueNode and not n.round_over:
                build_children(n)

    build_children(root)
    return root