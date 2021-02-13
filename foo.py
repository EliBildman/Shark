import networkx as nx 
import matplotlib.pyplot as plt 
   

# Driver code
conns = [('a', 'b'), ('b', 'c')]

G = nx.DiGraph()

for c in conns:
    for n in c:
        G.add_node(n)
    G.add_edge(*c, color='red')
    
        

nx.draw_networkx(G, node_color='white')
plt.show()

