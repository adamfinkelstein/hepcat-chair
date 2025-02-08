# Hepcat Chair

This repo contains code to help the SIGGRAPH PC Chair add data to Hepcat. There are four programs:

- `fake.py` - generates fake data in CSV files (papers, users, reviews, etc.) This is mostly simulating data that would otherwise be exported from Linklings. It is helpful for testing in Hepcat, since none of this data is sensitive.

- `chair.py` - reads either **fake** or **real** CSV files for papers and reviews, and exports the `chair.csv` file to be uploaded to Hepcat with review information for each paper. This computes an average score for sorting as well as a formatted string for display of the review information, for each paper.

- `chair_simple.py` - a basic version of `chair.py` added in 2025 that omits many of the unnecessary bells and whistles that were added over the preceding years due to mission creep. This version just reads the reviews file and writes a chair file with a simple average of the input score, and a common recommendation from the primary and secondary.

- `plot.py` - reads the file `stats.csv` (or whatever name) output by chair.py, and makes four histograms of the various types of score. This may be useful for the chair to set the bar in Hepcat, and to figure out how to compute sorting scores. Outputs a PNG showing the histograms.

## One-time setup

To set up the python virtual environment (one time)

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install numpy requests Faker
```

Later, to re-activate that environment in a new shell, simply:

```
source venv/bin/activate
```

## Running `fake.py`

Activate the virtual environment (above) and then run:

```
python3 fake.py [data_dir] [n_users|existing_users.csv] [n_papers] [default_passwd]
```

There are reasonable default values for these optional args. The second arg can be either an integer number of users, or a specific (typically real) users file to be used with otherwise fake data. The program creates the output directory data_dir if it does not already exist. This output directory will contain the following output files, mimicking what we might get out of Linklings:

- users.csv
- papers.csv
- conflicts.csv
- clusters.csv
- reviews.csv

It also produces these output files, for convenience:

- paper_rooms.csv - this and the following file would normally be produced by a separate optimization over the papers and reviewers if we were working with real data. But since it's all fake data, why not fake this randomly too.
- people_rooms.csv - see previous.
- history.csv - note this is just a convenience file to upload to Hepcat, to simulate the case that we are partway through the meeting.

## Running `chair.py`

Update: if you get a warning when you run `chair.py` that looks like `NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+` this appears to be about a dependency in the requests library and can be resulved by:

```
pip install urllib3==1.26.6
```

To run it, activate the virtual environment (above) and then run:

```
python chair.py --help
```

...to see the options / defaults.

The input files are:

- `papers.csv` - contains the list of papers (and crucially, whether they are journal-only, or dual-track).
- `reviews.csv` - contains the latest "status" for the papers, downloaded from Linklings (or fake, produced by the program above).

Note that the papers and reviews can also be given as URLs suitable for downloading directly from Linklings (but put double-quotes around them to avoid shell problem with special characters like ampersand).

This program produces the output file:

- `chair.csv` - contains four columns that update the information for each paper. It has the following format:

```
Submission ID,Sort Score,Status,Reviews
papers_101,-0.8,Tabled,"c[r, R, r, a, R!] j[a, a, A, R, r] bbs: Tabled"
papers_102,1.8,Journal,"j[A!, r, A, r, A] (journal only) bbs: Journal"
```

This program also optionally produces the output file:

- `stats.csv` - contains four columns that provide stats on conference and journal averages, to help the chair set the bar. It has the following format:

```
Submission ID,Dual Track,Conference Ave,Journal Ave
papers_101,False,0.0,-1.8
papers_102,False,0.0,3.4
papers_103,False,0.0,-1.8
papers_104,True,-2.6,0.6
papers_105,True,-3.4,-1.8
papers_106,True,0.6,-1.0
```

Notes on this data:

- As of SA23, the sort score for journal-only papers is the mean journal review score, while the sort score for dual-track paper is the mean of the conference review score.

- The optional argument `--ave_all` instructs the program to instead compute the sort score as a simple mean of all scores (still journal-only scores for journal-only submissions).

- The status is typically either:

  - (a) the recommendation of the primary and secondary, if they both provide the same recommendation, or
  - (b) Tabled.

- The Reviews column is simply a string representing all the review information together, as it should appear in Hepcat. Note that A! or R! is meant to put that letter in bold like: **A** and **R**.

## Running `chair_simple.py`

To run it, activate the virtual environment (above) and then run:

```
python chair_simple.py --help
```

...to see the options / defaults.

The input file is:

- `reviews.csv` - contains the latest "status" for the papers, downloaded from Linklings (or fake, produced by the "fake" program above).

## Running `plot.py`

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
