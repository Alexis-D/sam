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

    def insert(self, word, first=True):
        """Insert a single word (word) in the trie.

        first shouldn't be used, it's an internal parameter
        """

        if len(word):
            if first: # used as a sentinel to mark the end of the words
                      # otherwise words like "de" would be allowed if
                      # "deterrer" was in the trie
                word += '$'

            c, w = word[0], word[1:]
            if c in self.childs:
                self.childs[c].insert(w, False)
            else:
                self.childs.setdefault(c, Trie()).insert(w, False)

    def __contains__(self, word):
        """in keyword, return true if word is in the trie."""

        if len(word) == 0:
            return False

        if len(word) == 1:
            return word == '$'

        c, w = word[0], word[1:]

        if c in self.childs:
            return w in self.childs[c]

        elif '*' in self.childs:
            return True

        return False

