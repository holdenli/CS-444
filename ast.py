#!/usr/bin/python3

from utils.node import Node

def astize(parse_tree):

    def collapse(node):
        """
        recursive helper function for collapsing nodes
        """
        if type(node) is not Node:
            return

        newchildren = []
        for c in node.children:
            if c == node:
                collapse(c)
                newchildren.extend(c.children)
            else:
                newchildren.append(c)

        node.children = newchildren 

    """
    collapse nodes generated from one-or-more style grammar rules such as

    Rule=[Rule=[Rule=[Terminal] Terminal] Terminal] 

    to Rule=[Terminal, Terminal, Terminal]
    """
    # collapse breadth-first-search style
    nodes = [parse_tree]
    for node in nodes:
         collapse(node)
         nodes.extend(node.children)
