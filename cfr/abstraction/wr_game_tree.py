from .RoundNodes import DecisionNode, GameState, ValueNode
from .WRNodes import Conn, WRNatureNode
from .AGameNode import AGameNode
from .decision_tree import build_decision_tree
from .wr_map import load_file, save, NODE_FILE, TREE_FILE, TEST_NODES, TEST_TREE 

G_TREE_FILE = 'D:/dev/Shark/abstraction/caches/game_tree.dic'
TEST_G_TREE = 'D:/dev/Shark/abstraction/caches/t_game_tree.dic'


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
            
            game_node.get_info_set() #initilize info_set

        else:
            #send back value
            take = d_node.gamestate.pots[0] * (1 if p1_wr > p2_wr else (-1 if p2_wr > p1_wr else 0)) #TODO: estimated EV
            v_node = ValueNode(take, d_node.last_action)
            return AGameNode( parent, v_node, [p1_wr, p2_wr] )
            # for child in leaf_children:  
                #game_node.add_child( create_game_tree(child, d_tree, parent= game_node) )
                #changed to connect entire bottom of decision tree to next nature state
                #loses history past begining of round, but cuts down size of tree

        return game_node

    if n_tree.is_root:
        root = AGameNode(parent, n_tree, None)

        for c in n_tree.get_children():
            root.add_child( create_game_tree(c, d_tree, parent = root) )
    else:
        root = AGameNode(parent, n_tree, [n_tree.p1_wr.wr, n_tree.p2_wr.wr])
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

