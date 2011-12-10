#!/usr/bin/env python
#-*- coding: utf-8 -*-

import trie
import re
import unicodedata

def norm(s):
    return ''.join(x for x in unicodedata.normalize('NFD', s) if unicodedata.category(x) != 'Mn').lower()


if __name__ == '__main__':
    t = trie.Trie()

    with open('data/lexicon') as f:
        for l in f:
            t.insert(re.search(r'\w+\*?', l).group(0))

    with open('data/<put true path to unicode dict here>') as f:
        f.readline()

        for l in f:
            m = norm(re.search(r'\w+', l).group(0).lower())

            if m not in t:
                print('+' if re.search(r'Positiv', l) else '-', m)

