from nodes import WRNode, DecisionNode, GameState, ValueNode, Conn, WRNatureNode
from decision_tree import build_decision_tree
from wr_map import load, save, NODE_FILE, TREE_FILE, TEST_NODES, TEST_TREE 

G_TREE_FILE = 'D:/dev/Shark/abstraction/caches/game_tree.dic'
TEST_G_TREE = 'D:/dev/Shark/abstraction/caches/t_game_tree.dic'

strategy_profile = [
    {}, #p1 strats 
    {}  #p2 strats
]

info_sets = []

def p_action(info_set, action):
    if action.move.amount:
        return strategy_profile[action.player][info_set.id][action.move.name][str(action.move.amount)]
    else:
        strategy_profile[action.player][info_set.id][action.move.name]


#wrapper class for WRNatureNode and DecisionNode to make the tree to train on
class AGameNode():

    #parent: AGameNode | None, inner_node: WRNatureNode | DecisionNode, wrs: [float] | None, children = [(AGameNode, float)]
    def __init__(self, parent, inner_node, wrs, children = []):

        if type(inner_node) is not WRNatureNode and type(inner_node) is not DecisionNode and type(inner_node) is not ValueNode:
            raise Exception('wrong node type')

        self.is_nature = type(inner_node) is WRNatureNode
        self.is_value = type(inner_node) is ValueNode
        self.is_decision = type(inner_node) is DecisionNode

        self.parent = parent
        self.inner_node = inner_node
        self.children = children[:]
        self.wrs = wrs
        self.player = inner_node.gamestate.player() if  self.is_decision else -1
        self.is_round_end = self.is_decision and inner_node.round_over
        self.is_root = parent is None
        self.history = []

    #get info set containing this node, assumes this is decision node
    def get_info_set(self):
        return 1

    def get_children(self):
        return self.children

    def add_child(self, child):
        self.children.append(child)

    #gives transition prob to this node from parent
    def t(self):

        if self.is_nature is WRNatureNode:
            return self.inner_node.t
        
        else: #deicsion node or value node
            if self.parent.is_nature:
                return 1

            info_set = self.parent.get_info_set()
            return p_action(info_set, self.inner_node.last_action)
            #calculate based on strategy profile of player at parent node, or 1.0 if parent is nature

    #gets move history from last nature to here, TODO: make this go back to root when full tree is being explored
    def get_history(self):
        if self.history:
            return self.history

        curr = self
        while not curr.is_nature:
            self.history.insert(0, curr.inner_node.last_action)
            curr = curr.parent
        
        return self.history

#create a game tree of AGameNodes given a nature tree and deicsion tree
def create_game_tree(n_tree, d_tree, parent = None):
    
    #wraps a decision tree with AGameNodes with a given nature state
    def wrap_d_tree(p1_wr, p2_wr, d_node, parent, leaf_children):
        
        if type(d_node) is ValueNode:
            return AGameNode(parent, d_node, [p1_wr, p2_wr])

        if not d_node.round_over:
            game_node = AGameNode(parent, d_node, [p1_wr, p2_wr])
            for child in d_node.get_children():
                game_node.add_child( wrap_d_tree(p1_wr, p2_wr, child, game_node, leaf_children) )
        else:
            #send back value
            take = d_node.gamestate.pots[0] * (1 if p1_wr > p2_wr else -1)
            v_node = ValueNode(take, d_node.last_action)
            return AGameNode( parent, v_node, [p1_wr, p2_wr] )
            # for child in leaf_children:  
                #game_node.add_child( create_game_tree(child, d_tree, parent= game_node) )
                #changed to connect entire bottom of decision tree to next nature state
                #loses history past begining of round, but cuts down size of tree

        return game_node

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


    




n_size = tree_size(n_tree)

game_tree = create_game_tree(n_tree, d_tree)

print(game_tree)


# save(game_tree, G_TREE_FILE)

# g_tree = load(G_TREE_FILE)



