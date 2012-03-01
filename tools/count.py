#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os.path
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

    return (normalize(w) for w in _words_re.findall(s))


class Counter:
    def __init__(self, dict_path, dict_economy):
        self.pos = trie.Trie()
        self.neg = trie.Trie()
        self.eco = trie.Trie()

        with open(dict_path) as f:
            for l in f:
                sentiment, w, *_ = l.strip().split(' ')

                if sentiment == '+':
                    self.pos.insert(w)
                else:
                    self.neg.insert(w)

        with open(dict_economy) as f:
            for l in f:
                w, *_ = l.strip().split(' ')
                self.eco.insert(w)


    def process(self, filename):
        nw, p, n, d = 0, 0, 0, 0

        with open(filename) as f:
            for l in f:
                if l.startswith("==="):
                    f.readline() # date
                    f.readline() # source

                for w in words(l):
                    nw += 1
                    if w in self.eco:
                        d += 1
                    elif w in self.pos:
                        p += 1
                    elif w in self.neg:
                        n += 1

        return nw, p, n, d


if __name__ == '__main__':
    out_csv = 'data/frequencies.csv'
    c = Counter('data/lexicon', 'data/economy')

    with open(out_csv, 'w') as out:
        out.write('Date      ,   #words,     +++,     ---,  domain\n')
        for i, f in enumerate(sys.argv[1:], 1) :
            print('%4d/%4d' % (i, len(sys.argv) - 1), end='')
            sys.stdout.flush()
            print('\b' * 9, end='')
            nwords, positive, negative, domain = c.process(f)
            out.write('%s, %8d, %7d, %7d, %7d\n' %
                    (os.path.basename(f).replace('_', '/'),
                        nwords, positive, negative, domain))

