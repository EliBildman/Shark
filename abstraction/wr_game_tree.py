from nodes import WRNode, DecisionNode, GameState, ValueNode, Conn, WRNatureNode
from decision_tree import build_decision_tree
from wr_map import load, NODE_FILE



strategy_profile = [
    {}, #p1 strats 
    {}  #p2 strats
]

player_one_strat = {}
player_two_strat = {}

info_sets = []

#wrapper class for WRNatureNode and DecisionNode to make the tree to train on
class AGameNode():

    #parent: AGameNode | None, inner_node: WRNode | DecisionNode, wrs: [float] | None, children = [(AGameNode, float)]
    def __init__(self, parent, inner_node, wrs, children = []):
        self.parent = parent
        self.inner_node = inner_node
        self.children = children[:]
        self.wrs = wrs
        self.player = -1 if type(inner_node) is WRNode else (inner_node.gamestate.player())
        self.is_round_end = type(inner_node) is DecisionNode and inner_node.round_over

        if(type(self.inner_node) is not WRNatureNode and type(self.inner_node) is not DecisionNode):
            raise Exception('wrong node type')

    def info_set(self, player):
        pass

    #combine children with probs given nature prob and strat profiles
    def get_children(self):

        if self.children:
            return self._p_children()

        if type(self.inner_node) is WRNatureNode:
            p1_wr = self.inner_node.p1_wr.wr
            p2_wr = self.inner_node.p2_wr.wr
            self.children
        
        elif type(self.inner_node) is DecisionNode:
            pass

        return self.children

    def add_child(self, child):
        self.children.append(child)

#GOTTA FIGURE OUT HOW TO MAKE THIS TREE, PROLLY SHOULDN"T CONSTRUCT THE WHOLE THING

def create_game_tree(n_tree, d_tree, parent = None):

    def wrap_d_tree(p1_wr, p2_wr, d_node, parent):
        game_node = AGameNode(parent, d_node, [], [p1_wr, p2_wr])
        if type(d_node) is not ValueNode and not d_node.round_over:
            for child in d_node.get_children():
                game_node.add_child( wrap_d_tree(p1_wr, p2_wr, child, game_node) )
        return game_node

    node = AGameNode(parent, n_tree, None)




    # wrap_d_tree(0.5, 0.5, d_tree, None)

    # if node is None:
    #     root = AGameNode(None, n_map, )


n = 0

def f(node):
    global n
    if type(node) is DecisionNode and not node.round_over:
        for child in node.get_children():
            n += 1
            f(child)

n_map = load(NODE_FILE)
d_tree = build_decision_tree()

f(d_tree)

print(n)

# y = create_game_tree(None, None, d_tree)

# x = 1