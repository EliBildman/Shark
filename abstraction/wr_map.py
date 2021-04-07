import pickle
from pypokerengine.utils.card_utils import gen_cards, gen_deck, estimate_hole_card_win_rate
from execution_time import ExecutionTime
import matplotlib.pyplot as plt
from nodes import Conn, WRNode

e = ExecutionTime()

N_NODES = 21
N_LEVELS = 4
N_TESTS = 1000

NODE_FILE = 'D:/dev/Shark/abstraction/wr_nodes.dic'


#creates WRNode map
def create_wr_map():
    inc = 1 / (N_NODES - 1)
    nodes = [[WRNode(None)]]
    for level in range(1, N_LEVELS + 1):
        nodes.append([])
        
        for node_i in range(N_NODES):
            nodes[level].append( WRNode(inc * node_i) )

        for node_p in nodes[level - 1]:
            for node_c in nodes[level]:
                node_p.add_child(node_c)

    return nodes 

def save_nodes(nodes, filename):
    f = open(filename, 'wb')
    pickle.dump(nodes, f)
    f.close()

def load_nodes(filename):
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


def train(n_itterations):
    nodes = load_nodes(NODE_FILE)
    for i in range(n_itterations):
        if i % 100 == 0:
            print(i / n_itterations)
            save_nodes(nodes, NODE_FILE)
        sim_nature(nodes)
    save_nodes(nodes, NODE_FILE)


def plot(node):
    wrs = [ str(int(conn.child.wr * 100)) for conn in node.conns ]
    ps = [ conn.n for conn in node.conns ]
    plt.bar(wrs, ps)
    plt.show()


# train(10000)

nodes = load_nodes(NODE_FILE)

# plot(nodes[1][10])
plot(nodes[3][10])

