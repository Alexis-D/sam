#!/usr/bin/env python
#-*- coding: utf-8 -*-

import csv
import datetime

if __name__ == '__main__':
    cac = 'data/cac40.csv'
    freqs = 'data/frequencies.csv'
    out = 'data/highlow.csv'
    start = datetime.date(2004, 1, 1) # included
    end = datetime.date(2009, 4, 1) # excluded

    data = {}

    with open(cac) as f:
        next(f)
        reader = csv.reader(f)

        for row in reader:
            year, month, day = row[0].split('-')
            date = datetime.date(int(year), int(month), int(day))
            d = {}
            d['high'] = float(row[2])
            d['low'] = float(row[3])
            d['volume'] = int(row[5])
            d['close'] = float(row[4])
            data[date] = d

    with open(freqs) as f:
        next(f)
        reader = csv.reader(f)

        for row in reader:
            try:
                day, month, year = row[0].split('/')
                date = datetime.date(int(year), int(month), int(day))
            except:
                # bad data, i.e. impossible date
                continue

            d = data.setdefault(date, {})
            d['words'] = int(row[1])
            d['pos'] = int(row[2])
            d['neg'] = int(row[3])
            d['eco'] = int(row[4])
            d['pos_freq'] = d['pos'] / d['words']
            d['neg_freq'] = d['neg'] / d['words']
            d['eco_freq'] = d['eco'] / d['words']

    with open(out, 'w') as f:
        f.write('Date, #words, #positive, #negative, domain, pos freq, neg freq, domain freq, volume, close, high, low\n')

        for date in sorted(data):
            if start <= date < end:
                d = data[date]

                if 'close' in d:
                    f.write('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % (
                                date,
                                d['words'],
                                d['pos'],
                                d['neg'],
                                d['eco'],
                                d['pos_freq'],
                                d['neg_freq'],
                                d['eco_freq'],
                                d['volume'],
                                d['close'],
                                d['high'],
                                d['low'],
                                ))

