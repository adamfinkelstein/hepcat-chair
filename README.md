# Hepcat Chair

This repo contains code to help the SIGGRAPH PC Chair add data to Hepcat. There are two main programs:

- `fake.py` - generates fake data in CSV files (papers, users, reviews, etc.) This is mostly simulating data that would otherwise be exported from Linklings. It is helpful for testing in Hepcat, since none of this data is sensitive.

- `basic_chair.py` - This program reads the papers and reviews files and writes a chair file with a simple average of the input score, and a common recommendation from the primary and secondary.

There are also two other programs that have not been updated in a while and should probably be ignored:

- `old_chair.py` - out of date version of the chair program that had a bunch of complicated features no longer needed.

- `plot.py` - out of date - reads the file `stats.csv` (or whatever name) output by old_chair.py, and makes four histograms of the various types of score. This may be useful for the chair to set the bar in Hepcat, and to figure out how to compute sorting scores. Outputs a PNG showing the histograms.

## One-time setup

To set up the python virtual environment (one time)

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install numpy Faker
```

Later, to re-activate that environment in a new shell, simply:

```
source venv/bin/activate
```

## Running `fake.py`

Activate the virtual environment (above) and then run:

```
python3 fake.py --help
```

There are reasonable default values for these optional args. The program creates the output directory data_dir if it does not already exist. This output directory will contain the following output files, mimicking what we might get out of Linklings:

- users.csv
- papers.csv
- conflicts.csv
- clusters.csv
- reviews.csv

It also produces this output file too, for debugging:

- history.csv - note this is just a convenience file to upload to Hepcat, to simulate the case that we are partway through the meeting.

## Running `chair.py`

To run it, activate the virtual environment (above) and then run:

```
python chair.py --help
```

...to see the options / defaults.

The input files are:

- `papers.csv` - contains the list of papers (and crucially, whether they are journal-only, or dual-track).
- `reviews.csv` - contains the latest "status" for the papers, downloaded from Linklings (or fake, produced by the program above).

This program produces the output file:

- `chair.csv` - contains four columns that update the information for each paper. It has the following format:

```
Submission ID,Sort Score,Status,Reviews
papers_101,-0.8,Tabled,"c[r, R, r, a, R!] j[a, a, A, R, r] bbs: Tabled"
papers_102,1.8,Journal,"j[A!, r, A, r, A] (journal only) bbs: Journal"
```

## Running `basic_chair.py`

To run it, activate the virtual environment (above) and then run:

```
python chair_simple.py --help
```

...to see the options / defaults.

The input file is:

- `reviews.csv` - contains the latest "status" for the papers, downloaded from Linklings (or fake, produced by the "fake" program above).

## Running `plot.py` (out of date!)

Activate the virtual environment (above) and then run:

```
python plot.py [stats.csv] [hist.png]
```

In addition to saving a PNG showing the histograms, it will output some stats on the command line, like:

```
dual_conf has count 409 min -4.2 max 3.0 mean -0.0 median -0.2
dual_jour has count 409 min -4.6 max 2.2 mean -1.7 median -1.8
jour_jour has count 183 min -4.2 max 3.4 mean 0.4 median 0.6
dual_all has count 818 min -4.6 max 3.0 mean -0.9 median -1.0
```

(These are the actual numbers from SA23, just prior to the meeting.) The meanings of the categories are:

- `dual_conf` - Conference scores for dual-track submissions.
- `dual_jour` - Journal scores from dual-track submissions.
- `jour_jour` - Journal scores from journal-only submissions.
- `dual_all` - All scores from dual-track-submissions.
