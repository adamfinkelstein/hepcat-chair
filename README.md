# Hepcat Chair

This repo contains code to help the SIGGRAPH PC Chair add data to Hepcat. There are two programs:

* `fake.py` - generates fake data in CSV files (papers, users, reviews, etc. This is mostly simulating data that would otherwise be exported from Linklings. It is helpful for testing in Hepcat, since none of this data is sensitive.

* `chair.py` - reads either **fake** or **real** CSV files for papers and reviews, and exports the `chair.csv` file to be uploaded to Hepcat with review information for each paper. This computes an average score for sorting as well as a formatted string for display of the review information, for each paper.

## One-time setup

To set up the python virtual environment (one time)

```
python3 -m venv venv
source venv/bin/activate
pip install numpy
pip install requests
pip install Faker
```

Later, to re-activate that environment in a new shell, simply:

```
source venv/bin/activate
```

## Running `fake.py`

Activate the virtual environment (above) and then run:

```
python3 fake.py data_dir [n_users] [n_papers] [default_passwd]
```

This will produce the following output files, mimicking what we might get out of Linklings:

* users.csv
* papers.csv
* conflicts.csv
* clusters.csv
* reviews.csv

It also produces these output files, for convenience:

* paper_rooms.csv - this and the following file would normally be produced by a separate optimization over the papers and reviewers if we were working with real data. But since it's all fake data, why not fake this randomly too.
* people_rooms.csv - see previous.
* history.csv - note this is just a convenience file to upload to Hepcat, to simulate the case that we are partway through the meeting.

## Running `chair.py`

Activate the virtual environment (above) and then run:

```
python chair.py papers.csv reviews.csv chair.csv
```

The input files are:

* `papers.csv` - contains the list of papers (and crucially, whether they are journal-only, or dual-track).
* `reviews.csv` - contains the latest "status" for the papers, downloaded from Linklings (or fake, produced by the program above).

Note that the papers and reviews can also be given as URLs suitable for downloading directly from Linklings (but put double-quotes around them to avoid shell problem with special characters like ampersand). 

This program produces the output file:

* `chair.csv` - contains four columns that update the information for each paper. It has the following format:

```
Submission ID,Sort Score,Status,Reviews
papers_101,-0.8,Tabled,"c[r, R, r, a, R!] j[a, a, A, R, r] bbs: Tabled"
papers_102,1.8,Journal,"j[A!, r, A, r, A] (journal only) bbs: Journal"
```

Notes on this data:

* As of SA23, the sort score is computed as a simple mean of all scores (journal-only scores for journal-only submissions). 
* The status is typically either: 
	* (a) the recommendation of the primary and secondary, if they both provide the same recommendation, or 
	* (b) Tabled.
