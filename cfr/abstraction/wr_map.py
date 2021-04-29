import pickle
from pypokerengine.utils.card_utils import gen_cards, gen_deck, estimate_hole_card_win_rate
from execution_time import ExecutionTime
import matplotlib.pyplot as plt
from WRNodes import Conn, WRNode, WRNatureNode

e = ExecutionTime()

N_NODES = 2
N_LEVELS = 5
N_TESTS = 10

NODE_FILE = 'D:/dev/Shark/cfr/abstraction/caches/wr_nodes.dic'
TREE_FILE = 'D:/dev/Shark/cfr/abstraction/caches/wr_tree.dic'

TEST_NODES = 'D:/dev/Shark/cfr/abstraction/caches/t_nodes.dic'
TEST_TREE = 'D:/dev/Shark/cfr/abstraction/caches/t_tree.dic'


#creates WRNode map
def create_wr_map():
    inc = 1 / (N_NODES - 1)
    nodes = [[WRNode(0.5)]]
    for level in range(1, N_LEVELS + 1):
        nodes.append([])
        
        for node_i in range(N_NODES):
            nodes[level].append( WRNode(inc * node_i) )

        for node_p in nodes[level - 1]:
            for node_c in nodes[level]:
                node_p.add_child(node_c)

    return nodes 

def save(nodes, filename):
    f = open(filename, 'wb')
    pickle.dump(nodes, f)
    f.close()

def load(filename):
    f = open(filename, 'rb')
    nodes = pickle.load(f)
    f.close()
    return nodes

def get_node(wr, level):
    i = round( wr * (N_NODES - 1) )
    # print(i)
    return level[i]

@e.timeit
def sim_nature(nodes):
    root = nodes[0][0]
    deck = gen_deck()
    deck.shuffle()

    #deal
    hole = deck.draw_cards(2)
    wr = estimate_hole_card_win_rate(nb_simulation=N_TESTS, nb_player=2, hole_card=hole)
    deal_node = get_node(wr, nodes[1])
    root.adjust_for(deal_node)

    comm = []
    curr = deal_node
    i = 2
    for comm_deal in [3, 1, 1]:
        comm = comm + deck.draw_cards(comm_deal)
        wr = estimate_hole_card_win_rate(nb_simulation=N_TESTS, nb_player=2, hole_card=hole, community_card=comm)
        _next = get_node(wr, nodes[i])

        curr.adjust_for(_next)
        curr = _next
        i += 1

#creates 2-player tree out of map, with two maps
def create_nature_tree(wr_map, save_file):

    def rec_build_tree(node):
        # print(len(node.get_children()), node.is_final)
        for child in node.get_children():
            rec_build_tree(child)

    map_s = wr_map[0][0]
    root = WRNatureNode([map_s, map_s], 1)
    rec_build_tree(root)
    save(root, save_file)
    return root


def train(n_itterations, save_file, dump_nodes = False):
    if not dump_nodes:
        nodes = load(save_file)
    else:
        nodes = create_wr_map()
    for i in range(n_itterations):
        if i % 100 == 0:
            print(i / n_itterations)
            save(nodes, save_file)
        sim_nature(nodes)
    save(nodes, save_file)


def plot(node):
    wrs = [ str(int(conn.child.wr * 100)) for conn in node.conns ]
    ps = [ conn.n for conn in node.conns ]
    plt.bar(wrs, ps)
    plt.show()

if __name__ == '__main__':
    train(100, TEST_NODES, dump_nodes=True)
    _map = load(TEST_NODES)
    create_nature_tree(_map, TEST_TREE)