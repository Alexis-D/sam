#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import sys
import trie
import unicodedata

def normalize(w):
    """Convert an UTF-8 encoded string to a pure ASCII one.

    Also call lower on the word."""

    nfkd = unicodedata.normalize('NFKD', w)
    return ''.join(x for x in nfkd if unicodedata.category(x)[0] == 'L').lower()


_words_re = re.compile(r'\w+')
def words(s):
    """Returns all the words of a string."""

    return (normalize(w) for w in re.findall(_words_re, s))


class Counter:
    def __init__(self, dict_path):
        self.pos = trie.Trie()
        self.neg = trie.Trie()

        with open(dict_path) as f:
            for l in f:
                sentiment, w, *_ = l.strip().split(' ')

                if sentiment == '+':
                    self.pos.insert(w)
                else:
                    self.neg.insert(w)


    def process(self, filename):
        p, n = 0, 0

        with open(filename) as f:
            for l in f:
                if l.startswith("==="):
                    f.readline() # date
                    f.readline() # source

                for w in words(l):
                    if w in self.pos:
                        p += 1
                    elif w in self.neg:
                        n += 1

        return p, n


if __name__ == '__main__':
    out_csv = sys.argv[-1]

    c = Counter("data/lexicon")

    for f in sys.argv[1:]:
        positive, negative = c.process(f)
        print(f, positive, negative)

