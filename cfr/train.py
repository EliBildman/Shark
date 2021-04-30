
def prob_history(node, ignore_p = False):
    p = 1.0
    for n in node.get_history():
        if not ignore_p or n.player != node.player:
            p *= n.t()
    return p

def cf_value(node, sub_action = None):

    #recursively get EV of node to every possible term, adjusted for transition probs
    def value_to_term(n, p = 1.0):
        if n.is_value:
            return n.inner_node.value * p

        s = 0
        for child in n.get_children():
            s += value_to_term(child, p * child.t())
        return s

    if sub_action is None:
        return prob_history(node, ignore_p= True) * value_to_term(node)

    for child in node.get_children():
        if child.last_action == sub_action:
            # *1 here is symbolic to represent this is the subbed strat where this action is always taken
            return prob_history(node, ignore_p= True) * 1.0 * value_to_term(child)
    
def cf_regret_node(node, action):
    pass

def cf_regret_iset(iset, action):
    pass

