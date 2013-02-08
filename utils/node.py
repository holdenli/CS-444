#!/usr/bin/python3

import os
import sys

class Node:

    name = None
    token = None
    children = []

    def __init__(self):
        pass

    def first_token(self):
        if self.token != None:
            return self.token
        elif self.children: # empty lists are false
            return self.children[0].first_token()
        else:
            return None

if __name__ == "__main__":
    n = Node()
    n2 = Node()
    n2.token = "OMG"
    n.children = [n2]
    print(n.first_token())

