import sys
import numpy
import csv
import numpy as np
from matplotlib import pyplot

def read_csv_rows(reader):
    rows = []
    skip_header = True
    for row in reader:
        if skip_header:
            skip_header = False
            continue
        rows.append(row)
    return rows

def read_csv_from_file(fname):
    with open(fname, 'r') as f:
        reader = csv.reader(f)
        rows = read_csv_rows(reader)
        return rows

def get_conf_from_dual(rows):
    return [float(row[2]) for row in rows if row[1] == 'True']

def get_jour_from_dual(rows):
    return [float(row[3]) for row in rows if row[1] == 'True']

def get_jour_from_jour(rows):
    return [float(row[3]) for row in rows if row[1] == 'False']

def dump_stats(arr, name):
    minimum = 0
    maximum = 0
    mean = 0
    median = 0
    count = len(arr)
    if count:
        minimum = min(arr)
        maximum = max(arr)
        mean = round(np.mean(arr),1)
        median = np.median(arr)
    print(f'{name} has count {count} min {minimum} max {maximum} mean {mean} median {median}')

USE = 'python plot.py [stats.csv] [hist.png]'

def parse_args():
    ok = True
    stats_file = 'data/stats.csv'
    hist_file = 'hist.png'
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print(USE)
            ok = False
        else:
            stats_file = sys.argv[1]
    if len(sys.argv) > 2:
        hist_file = sys.argv[2]
    return ok, stats_file, hist_file

def main():
    ok, stats_file, hist_file = parse_args()
    if not ok:
        return
    rows = read_csv_from_file(stats_file)

    # read rows into score distribution arrays
    dual_conf = get_conf_from_dual(rows)
    dual_jour = get_jour_from_dual(rows)
    jour_jour = get_jour_from_jour(rows)
    dual_all = dual_conf + dual_jour

    # dump some stats on those arrays
    dump_stats(dual_conf, 'dual_conf')
    dump_stats(dual_jour, 'dual_jour')
    dump_stats(jour_jour, 'jour_jour')
    dump_stats(dual_all,  'dual_all')

    # mae histograms and save in image
    bins = numpy.linspace(-5, 5, 12)
    hatch_dual_conf = 2*'/'
    hatch_dual_jour = 2*'\\'
    hatch_jour_jour = '.'
    pyplot.hist(dual_conf, bins, label='dual_conf', hatch=hatch_dual_conf, edgecolor='black', alpha=0.5)
    pyplot.hist(dual_jour, bins, label='dual_jour', hatch=hatch_dual_jour, edgecolor='black', alpha=0.5)
    pyplot.hist(jour_jour, bins, label='jour_jour', hatch=hatch_jour_jour, edgecolor='black', alpha=0.5)
    pyplot.hist(dual_all, bins, label='dual_all', edgecolor='black', alpha=0.1)
    pyplot.legend(loc='upper right')
    # pyplot.show()
    pyplot.savefig(hist_file)

if __name__ == "__main__":
    main()
