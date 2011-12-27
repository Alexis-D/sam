#!/usr/bin/env python
#-*- coding: utf-8 -*-

from collections import Counter
from pprint import pprint
from queue import Queue
from threading import Thread

import re
import sys

words = re.compile(r'\w+', re.UNICODE)

def wc(q, filename):
    """Add a counter to the Queue q which count the word in the file filename.
    """

    with open(filename) as f:
        q.put(Counter((w.lower() for w in re.findall(words, f.read()))))

if __name__ == '__main__':
    q = Queue()
    threads = []

    for f in sys.argv[1:]:
        t = Thread(None, wc, None, (q, f,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    c = Counter()
    while not q.empty():
        c += q.get()

    pprint(c.most_common(10000))


