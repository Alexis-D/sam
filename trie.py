#!/usr/bin/env python
#-*- coding: utf-8 -*-

class Trie:
    """Represent a trie, with a special character * which match any suffix.
    e.g. increas* will match increase, increasing, increased and so on.
    """

    def __init__(self):
        self.childs = {}

    def iinsert(self, iterable):
        """Insert all words of iterable in the trie."""

        for w in iterable:
            self.insert(w)

    def insert(self, word):
        """Insert a single word (word) in the trie."""

        if len(word):
            c, w = word[0], word[1:]
            if c in self.childs:
                self.childs[c].insert(w)
            else:
                self.childs.setdefault(c, Trie()).insert(w)

    def __contains__(self, word):
        """in keyword, return true if word is in the trie."""

        if len(word) == 0:
            return True

        c, w = word[0], word[1:]

        if '*' in self.childs:
            return True

        elif c in self.childs:
            return w in self.childs[c]

        return False

