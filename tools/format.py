#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os.path
import re
import time
import sys

if __name__ == '__main__':
    # took the file downloaded from lexis nexis, and reformat them
    # to be easier to use
    # (this script is quick 'n dirty)

    out_dir = 'data/data/'
    day, month, year = 0, 0, 0

    docs = re.compile(r'\d+ of \d+ documents', re.I)
    copy = re.compile(r'copyright', re.I)

    # for each filename
    for f in sys.argv[1:]:
        out = ''
        print(f)
        with open(f) as f:
            for l in f:
                # empty line
                if not l.strip():
                    continue

                # ok begin of a single article
                elif re.search(docs, l):
                    l = f.readline()

                    while not l.strip():
                        l = f.readline()

                    src = l.strip()

                    l = f.readline()

                    while not l.strip():
                        l = f.readline()

                    try:
                        day, month, year = l.split()
                        day = int(day)
                        year = int(year)

                        # time module & locale doesn't seemed to want to work
                        # properly so quick hack
                        month = 1 + ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
                                    'août', 'septembre', 'octobre', 'novembre', 'décembre'].index(month)
                    except:
                        # english date format
                        t = time.strptime(l.strip(), '%B %d, %Y')
                        day = t.tm_mday
                        month = t.tm_mon
                        year = t.tm_year

                    out += '%d/%d/%d\n' % (day, month, year)
                    out += '%s\n' % src

                    l = f.readline()

                    while not re.search(copy, l):
                        if l.strip():
                            if not l.split()[0].isupper():
                                out += l

                        l = f.readline()

                    # consume the second copyright line (all right reserved)
                    f.readline()
                    out += '===\n'

        with open(os.path.join(out_dir, '%02d_%02d_%04d' % (day, month, year)), 'w') as f:
            f.write(out)

