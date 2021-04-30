from RoundNodes import DecisionNode, ValueNode, GameState

RAISE_AMOUNTS = [1]
PLAYERS = 2
BLINDS = [0.5, 1]
MAX_BET = 2

def build_decision_tree():

    init_state = GameState(PLAYERS, BLINDS, [0, 0], 0, MAX_BET)
    root = DecisionNode(None, init_state, RAISE_AMOUNTS)

    def build_children(node):
        for n in node.get_children():
            if type(n) != ValueNode and not n.round_over:
                build_children(n)

    build_children(root)
    return root

if __name__ == '__main__':
    x = build_decision_tree()