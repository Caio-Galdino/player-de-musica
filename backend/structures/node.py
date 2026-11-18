class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class DoublyNode:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

class HashNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 0