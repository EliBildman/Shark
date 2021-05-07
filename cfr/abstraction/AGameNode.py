from .WRNodes import WRNode, WRNatureNode
from .RoundNodes import DecisionNode, ValueNode, WRInfoSet

# strategy_profile = [
#     {}, #p1 strats 
#     {}  #p2 strats
# ]

# def p_action(info_set, action):
#     if not strategy_profile[action.player][info_set.id]:
#         strategy_profile[action.player][info_set.id] = {}
#     if action.move.amount:
#         return strategy_profile[action.player][info_set.id][action.move.name][str(action.move.amount)]
#     else:
#         strategy_profile[action.player][info_set.id][action.move.name]

info_sets = []

#wrapper class for WRNatureNode and DecisionNode to make the tree to train on
class AGameNode():

    #parent: AGameNode | None, inner_node: WRNatureNode | DecisionNode, wrs: [float] | None, children = [(AGameNode, float)]
    def __init__(self, parent, inner_node, wrs, children = []):

        if type(inner_node) is not WRNatureNode and type(inner_node) is not DecisionNode and type(inner_node) is not ValueNode:
            raise Exception('wrong node type')

        self.is_nature = type(inner_node) is WRNatureNode
        self.is_value = type(inner_node) is ValueNode
        self.is_decision = type(inner_node) is DecisionNode
        
        self.is_root = parent is None
        self.is_round_end = self.is_decision and inner_node.round_over

        self.parent = parent
        self.inner_node = inner_node
        self.children = children[:]
        self.wrs = wrs
        self.player = inner_node.gamestate.player() if self.is_decision else -1
        self.history = []
        self.info_set = None

        # if self.is_decision:
        #     self.get_info_set()

    #get info set containing this node, assumes this is decision node
    def get_info_set(self):

        if self.info_set:
            return self.info_set

        for info_set in info_sets: #look for existing info set
            if info_set.matches_node(self):
                self.info_set = info_set
                info_set.add_node(self)

        if self.info_set is None: #didnt find one
            new_info_set = WRInfoSet(self)
            new_info_set.add_node(self)
            self.info_set = new_info_set
            info_sets.append(new_info_set)

        return self.info_set

    def get_children(self, i = None):
        if i is None:
            return self.children
        else:
            return self.children[i]

    def add_child(self, child):
        self.children.append(child)

    #gives transition prob to this node from parent
    def t(self):

        if self.is_nature:
            return self.inner_node.t
        
        else: #deicsion node or value node
            if self.parent.is_nature:
                return 1.0

            info_set = self.parent.get_info_set()
            return info_set.p_action(self.inner_node.last_action)
            # return p_action(info_set, self.inner_node.last_action)
            #calculate based on strategy profile of player at parent node, or 1.0 if parent is nature

    #gets move history from last nature to here
    #if player_per only gets info for active player
    def get_history(self):
        if self.history:
            return self.history

        curr = self
        while not curr.is_root:
            self.history.insert(0, curr)
            curr = curr.parent
        
        return self.history

    def __str__(self):
        _type = 'nature' if self.is_nature else ('decision' if self.is_decision else 'value')
        return 'AGameNode(wrs: ' + str(self.wrs) + ', type: ' + _type + ', last_action: ' + (str(self.inner_node.last_action) if not self.is_nature else 'N/A') + ')'