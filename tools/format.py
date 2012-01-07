#!/usr/bin/env python
#-*- coding: utf-8 -*-

import glob
import os.path
import re
import sys
import time

if __name__ == '__main__':
    # took the file downloaded from lexis nexis, and reformat them
    # to be easier to use
    # (this script is quick 'n dirty)

    out_dir = sys.argv[-1]
    day, month, year = 0, 0, 0

    docs = re.compile(r'\d+ of \d+ documents', re.I)
    copy = re.compile(r'copyright', re.I)

    for f in glob.glob(os.path.join(out_dir, '*')):
        os.unlink(f)

    # for each filename
    for i, f in enumerate(sys.argv[1:-1]):
        out = ''
        print('%4d/%4d' % (i + 1, len(sys.argv) - 1), end='')
        print('\b' * 9, end='')
        # if not flushed, won't be printed until '\n'
        sys.stdout.flush()

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
                        day, month, year, *_ = l.split()
                        day = int(day)
                        year = int(year)

                        # time module & locale doesn't seemed to want to work
                        # properly so quick hack
                        french_months = ['janvier', 'février', 'mars', 'avril',
                                         'mai', 'juin', 'juillet', 'août',
                                         'septembre', 'octobre', 'novembre',
                                         'décembre']
                        month = 1 + french_months.index(month.lower())
                    except:
                        # english date format
                        try:
                            t = time.strptime(l.strip(), '%B %d, %Y')
                            day = t.tm_mday
                            month = t.tm_mon
                            year = t.tm_year
                        except:
                            # Lundi 12 Juin 2006 12:20 PM CEST
                            _, day, month, year, *_ = l.strip().lower().split()
                            day = int(day)
                            year = int(year)
                            month = 1 + french_months.index(month)

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

        with open(os.path.join(out_dir, '%02d_%02d_%04d' % (day, month, year)), 'a') as f:
            f.write(out)

    print()

