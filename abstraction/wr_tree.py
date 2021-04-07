from nodes import WRNode, DecisionNode, GameState, ValueNode

# NODES_PER_LEVEL = [10, 5, 5, 5]
RAISE_AMOUNTS = [0.5, 1, 2, 5]

# #attach layer of n_children wrnodes to parent
# def attach_layer(parent, n_children):
#     for i in range(1, n_children + 1):
#         wr = (1.0 / (n_children + 1)) * i
#         n = WRNode(parent, wr)
#         parent.add_child(n)

# #create tree with children[i] WRNode children per parent in level i
# #returns root of tree
# def create_WR_tree(children, root = None):

#     if root is None:
#         root = WRNode(None, 0.5)

#     if len(children) > 0:
#         attach_layer(root, children[0])
#         children = children[1:]

#         for child in root.get_children():
#             create_WR_tree(children, root=child)
    
#     return root

#create abstracted decision tree where players can (FOLD, CALL, RAISE n for n in RAISE_AMOUNTS )
def build_decision_tree():

    init_state = GameState(2, [0.5, 1], [0, 0], 0, 10)
    root = DecisionNode(None, init_state, RAISE_AMOUNTS)

    def build_children(node):
        for n in node.get_children():
            if type(n) != ValueNode and not n.round_over:
                build_children(n)

    build_children(root)
    return root


class AGameNode():

    def __init__(self, parent, inner_node, children = []):
        self.inner_node = inner_node
        self.children = childnre[:]

    def info_set(self, player):
        pass

    def _find_children(self):
        children = []
        if type(self.inner_node) is WRNode:
            children = []

        elif type(self.inner_node) is DecisionNode:
            pass

def create_game_tree(n_tree, d_tree):

    root = AGameNode(None, n_tree)


nature_tree = create_WR_tree(NODES_PER_LEVEL)
dec_tree = build_decision_tree()

