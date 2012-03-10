#!/usr/bin/env python2
#-*- coding: utf-8 -*-

import ar
import lm

def predict(x, lag=7):
    x, y = ar.arLMmodel(x, lag=lag)
    return lm.ols(x, y).betas

if __name__ == '__main__':
    import csv

    with open('data/merged.csv') as f:
        _ = next(f)

        reader = csv.reader(f)
        dates, pos, neg, posneg, vol, close = [], [], [], [], [], []

        for row in reader:
            c = row[-1]

            if c.strip():
                dates.append(row[0])
                pos.append(float(row[5]))
                neg.append(float(row[6]))
                posneg.append(pos[-1] / neg[-1])
                vol.append(float(row[8]))
                close.append(float(c))

    width = int(.9 * len(close))
    lag = 7
    vol_coeffs = predict(vol[:width], lag=lag)
    close_coeffs = predict(close[:width], lag=lag)

    with open('data/arlm.csv', 'w') as out:
        out.write('Date, pos freq, neg freq, pos / neg, '
                  'volume, volume prev, volume epsilon, '
                  'close, close prev, close epsilon\n')

        for i, (c, v) in enumerate(zip(close[width:], vol[width:]), start=width):
            vol_prev = vol_coeffs[0] + sum(vol_coeffs[j] * vol[i - j]
                    for j in range(1, lag + 1))
            close_prev = close_coeffs[0] + sum(close_coeffs[j] * close[i - j]
                    for j in range(1, lag + 1))
            out.write('%s, %f, %f, %f, %f, %f, %f, %f, %f, %f\n' %
                    (dates[i], pos[i], neg[i], posneg[i], v, vol_prev,
                    v - vol_prev, c, close_prev, c - close_prev))

