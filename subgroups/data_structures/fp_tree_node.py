# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a generic FPTree Node.
"""

from subgroups.core.selector import Selector
from pandas import DataFrame

class FPTreeNode(object):
    """This class represents a generic FPTree Node.
    
    :type selector: Selector
    :param selector: the Selector which is represented by this node.
    :type counters: list[int]
    :param counters: a list with the needed counters (the meaning of its elements depends on the situation). IMPORTANT: we assume that this list only contains values of type 'int'.
    :type node_link: FPTreeNode or NoneType
    :param node_link: the next node in the FPTree with the same selector as this one (or None if it does not exist).
    """
    
    __slots__ = "_selector", "_counters", "_node_link", "_childs", "_parent"
    
    def __init__(self, selector, counters, node_link):
        if type(selector) is not Selector:
            raise TypeError("The type of the parameter 'selector' must be 'Selector'.")
        if type(counters) is not list:
            raise TypeError("The type of the parameter 'counters' must be 'list'.")
        if (type(node_link) is not FPTreeNode) and (node_link is not None):
            raise TypeError("The type of the parameter 'node_link' must be 'FPTreeNode' or 'NoneType'.")
        self._selector = selector
        self._counters = counters
        self._node_link = node_link
        self._childs = dict() # The child nodes of the current node. The dictionary key is a Selector and the dictionary value is a FPTreeNode.
        self._parent = None
    
    def _get_selector(self):
        return self._selector
    
    def _get_counters(self):
        return self._counters
    
    def _get_node_link(self):
        return self._node_link
    
    def _set_selector(self, selector):
        if type(selector) is not Selector:
            raise TypeError("The type of the parameter 'selector' must be 'Selector'.")
        self._selector = selector
    
    def _set_counters(self, counters):
        if type(counters) is not list:
            raise TypeError("The type of the parameter 'counters' must be 'list'.")
        self._counters = counters
    
    def _set_node_link(self, node_link):
        if (type(node_link) is not FPTreeNode) and (node_link is not None):
            raise TypeError("The type of the parameter 'node_link' must be 'FPTreeNode' or 'NoneType'.")
        self._node_link = node_link
    
    def _get_number_of_children(self):
        return len(self._childs)
    
    def _get_parent(self):
        return self._parent
    
    def _set_parent(self, parent):
        if (type(parent) is not FPTreeNode) and (parent is not None):
            raise TypeError("The type of the parameter 'parent' must be 'FPTreeNode' or 'NoneType'.")
        self._parent = parent
    
    selector = property(_get_selector, _set_selector, None, "The Selector which is represented by this node.")
    counters = property(_get_counters, _set_counters, None, "A list with the needed counters (the meaning of its elements depends on the situation). IMPORTANT: we assume that this list only contains values of type 'int'.")
    node_link = property(_get_node_link, _set_node_link, None, "The next node in the FPTree with the same selector as this one (or None if it does not exist).")
    number_of_children = property(_get_number_of_children, None, None, "The number of children of this node.")
    parent = property(_get_parent, _set_parent, None, "The parent of this node")
    
    def add_child(self, child):
        """Method to add a child node to the current node. The current node will be the parent of the added child. IMPORTANT: if the child already exists, a KeyError exception is raised.
        
        :type child: FPTreeNode
        :param child: the child node which is added.
        """
        if (type(child) is not FPTreeNode):
            raise TypeError("The type of the parameter 'child' must be 'FPTreeNode'.")
        if (child.selector in self._childs):
            raise KeyError("This child already exists.")
        else:
            child._parent = self
            self._childs[child.selector] = child
    
    def delete_child(self, child):
        """Method to delete a child node from the current node. The current node will not be the parent of the deleted child anymore. IMPORTANT: if the child does not exist, a KeyError exception is raised.
        
        :type child: FPTreeNode
        :param child: the child node which is deleted.
        """
        if (type(child) is not FPTreeNode):
            raise TypeError("The type of the parameter 'child' must be 'FPTreeNode'.")
        if (child.selector not in self._childs):
            raise KeyError("This child does not exist.")
        else:
            child._parent = None
            del self._childs[child.selector]
    
    def has_this_child(self, node):
        """Method to check whether the node passed by parameter is a child of this one.
        
        :type node: FPTreeNode
        :param node: the node which is checked.
        :rtype: bool
        :return: whether the node passed by parameter is a child of this one.
        """
        if (type(node) is not FPTreeNode):
            raise TypeError("The type of the parameter 'node' must be 'FPTreeNode'.")
        return (node.selector in self._childs)
    
    def is_child_of(self, node):
        """Method to check whether the node passed by parameter is the parent of this one or to check whether it does not exist parent (passing None by parameter).
        
        :type node: FPTreeNode or NoneType
        :param node: the node which is checked or None.
        :rtype: bool
        :return: whether the node passed by parameter is the parent of this one or whether it does not exist parent (if None was passed by parameter).
        """
        if (type(node) is not FPTreeNode) and (node is not None):
            raise TypeError("The type of the parameter 'node' must be 'FPTreeNode' or 'NoneType'.")
        return (id(self._parent) == id(node))
    
    def get_child_by_selector(self, selector):
        """Method to get the child whose selector is passed by parameter.
        
        :type selector: Selector
        :param selector: the selector which is checked.
        :rtype: FPTreeNode or NoneType
        :return: the child whose selector is passed by parameter or None if it does not exist.
        """
        try:
            return self._childs[selector]
        except KeyError:
            return None 
    
    def __str__(self):
        final_str = "{id: " + str(id(self)) + ", selector: " + str(self._selector) + ", counters: " + str(self._counters)
        if self._node_link == None:
            return final_str + ", node_link_id: None}"
        return final_str + ", node_link_id: " + str(id(self._node_link)) + "}"
    
    def tree_as_str(self, current_depth=0):
        """Method to print as str the current node and the complete subtree from the current node.
        :type current_depth: int
        :param current_depth: the depth of the current node. By default, 0.
        :rtype: str
        :return: the printed result (the current node and the complete subtree from the current node).
        """
        result = ""
        # Print the current node.
        if current_depth > 0:
            result = result + ("    "*(current_depth-1)) + ("|--- ")
        result = result + str(self) + "\n"
        # Recursive calls.
        for key in self._childs:
            result = result + self._childs[key].tree_as_str(current_depth+1)
        return result
