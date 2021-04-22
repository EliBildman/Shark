from nodes import WRNode, DecisionNode, GameState, ValueNode, Conn, WRNatureNode
from decision_tree import build_decision_tree
from wr_map import load, NODE_FILE, TREE_FILE, save



strategy_profile = [
    {}, #p1 strats 
    {}  #p2 strats
]

player_one_strat = {}
player_two_strat = {}

info_sets = []

#wrapper class for WRNatureNode and DecisionNode to make the tree to train on
class AGameNode():

    #parent: AGameNode | None, inner_node: WRNatureNode | DecisionNode, wrs: [float] | None, children = [(AGameNode, float)]
    def __init__(self, parent, inner_node, wrs, children = []):

        if type(inner_node) is not WRNatureNode and type(inner_node) is not DecisionNode:
            raise Exception('wrong node type')

        self.parent = parent
        self.inner_node = inner_node
        self.children = children[:]
        self.wrs = wrs
        self.is_nature = type(inner_node) is WRNatureNode
        self.player = -1 if self.is_nature else (inner_node.gamestate.player())
        self.is_round_end = type(inner_node) is DecisionNode and inner_node.round_over
        self.is_root = parent is None
        self.history = []

    #get info set containing this node
    def info_set(self, player):
        pass

    def get_children(self):
        return self.children

    def add_child(self, child):
        self.children.append(child)

    #gives transition prob to this node from parent
    def t(self):

        if self.is_nature is WRNatureNode:
            return self.inner_node.t
        
        else: #deicsion node
            pass #calculate based on strategy profile of player at parent node, or 1.0 if parent is nature

    #gets move history from last nature to here, TODO: make this go back to root when full tree is being explored
    def get_history(self):
        if self.history:
            return self.history

        curr = self
        while not curr.is_nature:
            self.history.insert(0, curr.inner_node.last_move)
        
        return self.history

n = 0
n_size = 0

#create a game tree of AGameNodes given a nature tree and deicsion tree
def create_game_tree(n_tree, d_tree, parent = None):
    #wraps a decision tree with AGameNodes with a given nature state
    def wrap_d_tree(p1_wr, p2_wr, d_node, parent, leaf_children):
        
        if type(d_node) is ValueNode:
            return d_node

        game_node = AGameNode(parent, d_node, [p1_wr, p2_wr])

        if not d_node.round_over:
            for child in d_node.get_children():
                game_node.add_child( wrap_d_tree(p1_wr, p2_wr, child, game_node, leaf_children) )
        else:
            for child in leaf_children:
                # game_node.add_child( create_game_tree(child, d_tree, parent= game_node) )
                game_node.add_child( child ) 
                #changed to connect entire bottom of decision tree to next nature state
                #loses history past begining of round, but cuts down size of tree

        return game_node

    global n
    n += 1
    p = (n / n_size) * 100
    if n % 1000 == 0:
        print(p)

    root = AGameNode(parent, n_tree, None)
    root.add_child( wrap_d_tree(n_tree.p1_wr.wr, n_tree.p2_wr.wr, d_tree, root, n_tree.get_children()) )

    for c in n_tree.get_children():
        create_game_tree(c, d_tree, parent = root)

    return root


def tree_size(n):
    if type(n) is ValueNode:
        return 1
    c = n.get_children()
    # if not c:
    #     return 1
    num = 1
    for child in c:
        num += tree_size(child)
    return num

# n_tree = load(TREE_FILE)
# d_tree = build_decision_tree()

# n_size = tree_size(n_tree)
# d_size = tree_size(d_tree)

# game_tree = create_game_tree(n_tree, d_tree)
# save(game_tree, 'game_tree.dic')

g_tree = load('game_tree.dic')

print( tree_size(g_tree) )