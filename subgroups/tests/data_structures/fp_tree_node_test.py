# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'data_structures/fp_tree_node.py'.
"""

from subgroups.data_structures.fp_tree_node import FPTreeNode
from subgroups.core.selector import Selector
from subgroups.core.operator import Operator

def test_FPTreeNode():
    # Root.
    selector1 = Selector("name", Operator.EQUAL, "value1")
    node1 = FPTreeNode(selector1, [1], None)
    assert (node1.selector == selector1)
    assert (node1.counters == [1])
    assert (node1.node_link == None)
    assert (str(node1) == "[id: " + str(id(node1)) + ", selector: name = 'value1', counters: [1], node_link_id: None]")
    node1.counters[0] = node1.counters[0] + 1
    assert (node1.counters == [2])
    assert (node1.node_link == None)
    assert (str(node1) == "[id: " + str(id(node1)) + ", selector: name = 'value1', counters: [2], node_link_id: None]")
    # Childs of root.
    selector2 = Selector("att1", Operator.EQUAL, "value2")
    node2 = FPTreeNode(selector2, [2], None)
    assert (node2.selector == Selector("att1", Operator.EQUAL, "value2"))
    assert (node2.counters == [2])
    selector3 = Selector("att2", Operator.EQUAL, "value3")
    node3 = FPTreeNode(selector3, [3], None)
    selector4 = Selector("att2", Operator.EQUAL, "value3")
    node4 = FPTreeNode(selector4, [4], None)
    selector5 = Selector("att3", Operator.EQUAL, "value5")
    node5 = FPTreeNode(selector5, [5], None)
    # Childs of 'node3'.
    selector6 = Selector("att1", Operator.EQUAL, "value6")
    node6 = FPTreeNode(selector6, [6], None)
    selector7 = Selector("att2", Operator.EQUAL, "value7")
    node7 = FPTreeNode(selector7, [7], None)
    # Add child nodes.
    node1.add_child(node2)
    node1.add_child(node3)
    try:
        node1.add_child(node4) # This node will not be inserted because it has the same selector as node3.
        assert (False)
    except KeyError:
        assert (True)
    node1.add_child(node5)
    assert (node1.number_of_children == 3)
    node3.add_child(node6)
    node3.add_child(node7)
    assert (node3.number_of_children == 2)
    assert (node6.number_of_children == 0)
    # Check if a node has a child.
    assert (node1.has_this_child( node3 ))
    assert (not node1.has_this_child( node7 ))
    assert (node3.has_this_child( node7 ))
    assert (not node3.has_this_child( node1 ))
    assert (not node3.has_this_child( node2 ))
    # Check the parents.
    assert (node1.is_child_of( None ))
    assert (node2.is_child_of( node1 ))
    assert (node3.is_child_of( node1 ))
    assert (node4.is_child_of( None ))
    assert (node5.is_child_of( node1 ))
    assert (node6.is_child_of( node3 ))
    assert (node7.is_child_of( node3 ))
    assert (id(node1.parent) == id( None ))
    assert (id(node2.parent) == id( node1 ))
    assert (id(node3.parent) == id( node1 ))
    assert (id(node4.parent) == id( None ))
    assert (id(node5.parent) == id( node1 ))
    assert (id(node6.parent) == id( node3 ))
    assert (id(node7.parent) == id( node3 ))
    # Get child nodes by selector.
    assert ( id(node1.get_child_by_selector( selector2 )) == id(node2))
    assert ( id(node1.get_child_by_selector( selector3 )) == id(node3))
    assert ( id(node1.get_child_by_selector( selector5 )) == id(node5))
    assert ( id(node3.get_child_by_selector( selector6 )) == id(node6))
    assert ( id(node3.get_child_by_selector( selector7 )) == id(node7))
    # Delete child nodes.
    node1.delete_child(node5)
    try:
        node1.delete_child(node5) # This node does not exist anymore.
        assert (False)
    except KeyError:
        assert (True)
    assert(node1.number_of_children == 2)
    node1.add_child(node5)
    assert(node1.number_of_children == 3)
