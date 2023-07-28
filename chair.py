import sys
import csv
import requests

# globals
verbose = False

def get_indices(arr, indices):
    return [ arr[i] for i in indices ]

def read_csv_rows(reader, indices):
    rows = []
    skip_header = True
    for row in reader:
        if skip_header:
            skip_header = False
            continue
        if indices:
            row = get_indices(row, indices)
        rows.append(row)
    return rows

def read_csv_from_url(url, indices):
    response = requests.get(url)
    response.raise_for_status()  # Check for any HTTP errors
    content = response.text # Decode the response content as text
    reader = csv.reader(content.splitlines())
    rows = read_csv_rows(reader, indices)
    return rows

def read_csv_from_file(fname, indices):
    with open(fname, 'r') as f:
        reader = csv.reader(f)
        rows = read_csv_rows(reader, indices)
        return rows

def read_csv(path, indices = None):
    if path.startswith("http"):
        return read_csv_from_url(path, indices)
    return read_csv_from_file(path, indices)

# papers: Submission ID,Thumbnail URL,Title,Area,Dual Track,Abstract
# pull out: ID, Dual
def read_papers(papers_file):
    all_pids = []
    dual_pids = []
    indices = [0, 4]
    rows = read_csv(papers_file, indices)
    for pid, dual in rows:
        all_pids.append(pid)
        if dual == 'yes':
            dual_pids.append(pid)
    return all_pids, dual_pids

# reviews: Submission ID,Role,Conference Score,Journal Score,Expertise,Final Recommendation
def read_reviews(reviews_file):
    reviews = {}
    rows = read_csv(reviews_file)
    for row in rows:
        pid = row.pop(0)
        if pid not in reviews:
            reviews[pid] = []
        reviews[pid].append(row)
    return reviews

def to_int(s):
    if not s:
        return 0
    return int(round(float(s)))

def format_status(code):
    code = to_int(code)
    if code < 0:
        return 'Reject'
    elif code > 1:
        return 'Journal'
    elif code == 1:
        return 'Conference'
    else:
        return 'Tabled'

def get_status_from_review(row):
    if len(row) < 5:
        return 'Tabled'
    return format_status(row[4])

def get_status_from_pri_sec(pid_revs):
    status = 'Tabled'
    if len(pid_revs) > 1:
        status0 = get_status_from_review(pid_revs[0])
        status1 = get_status_from_review(pid_revs[1])
        if status0 == status1:
            status = status0
    return status

# note that R! and A! will be made bold in the GUI
score_codes = { -5: 'R!', -3: 'R', -1: 'r', 1: 'a', 3: 'A', 5: 'A!'}

def format_score_codes(s):
    if s in score_codes:
        return score_codes[s]
    return '?'

def format_score_list(leader, scores):
    scores = [ format_score_codes(s) for s in scores]
    scores = ', '.join(scores)
    scores = f'{leader}[{scores}]'
    return scores

def scores_ave(scores):
    ave = sum(scores) / len(scores)
    ave = round(ave, 3)
    return ave

def get_review_ave(conf_scores, jour_scores, pid_is_dual, ave_all):
    if pid_is_dual and ave_all:
        all_scores = conf_scores + jour_scores
    elif pid_is_dual:
        all_scores = conf_scores
    else:
        all_scores = jour_scores
    ave = scores_ave(all_scores)
    return ave

# Submission ID,Sort Score,Status,Reviews
def format_pid_with_reviews(pid, pid_is_dual, pid_revs, ave_all):
    pid_revs.sort(key=lambda row: row[0]) # sort by role (first column)
    status = get_status_from_pri_sec(pid_revs)
    conf_scores = [to_int(row[1]) for row in pid_revs]
    jour_scores = [to_int(row[2]) for row in pid_revs]
    ave = get_review_ave(conf_scores, jour_scores, pid_is_dual, ave_all)
    jour_scores = format_score_list('j', jour_scores)
    if pid_is_dual:
        conf_scores = format_score_list('c', conf_scores)
        reviews = f'{conf_scores} {jour_scores} bbs: {status}'
    else:
        reviews = f'{jour_scores} (journal only) bbs: {status}'
    line = f'{pid},{ave},{status},"{reviews}"\n'
    return line

def format_pid_without_reviews(pid):
    return f'{pid},0,T,"(Has no reviews and is missing score.)"\n'

def get_conf_jour_ave(pid_revs):
    conf_scores = [to_int(row[1]) for row in pid_revs]
    jour_scores = [to_int(row[2]) for row in pid_revs]
    conf_ave = scores_ave(conf_scores)
    jour_ave = scores_ave(jour_scores)
    return conf_ave, jour_ave

def write_file(fname, contents):
    path = f'{fname}'
    with open(path, 'w') as f:
        f.write(contents)

def write_chair(all_pids, dual_pids, reviews, ave_all, fname):
    lines = 'Submission ID,Sort Score,Status,Reviews\n'
    for pid in all_pids:
        pid_is_dual = pid in dual_pids
        pid_revs = None
        if pid in reviews:
            pid_revs = reviews[pid]
            lines += format_pid_with_reviews(pid, pid_is_dual, pid_revs, ave_all)
        else:
            lines += format_pid_without_reviews(pid)
    write_file(fname,lines)

def write_stats(all_pids, dual_pids, reviews, fname):
    lines = 'Submission ID,Dual Track,Conference Ave,Journal Ave\n'
    for pid in all_pids:
        pid_is_dual = pid in dual_pids
        pid_revs = None
        if pid not in reviews:
            continue
        pid_revs = reviews[pid]
        conf_ave, jour_ave = get_conf_jour_ave(pid_revs)
        lines += f'{pid},{pid_is_dual},{conf_ave},{jour_ave}\n'
    write_file(fname,lines)

def write_outputs(all_pids, dual_pids, reviews, ave_all, chair_file, stats_file):
    write_chair(all_pids, dual_pids, reviews, ave_all, chair_file)
    write_stats(all_pids, dual_pids, reviews, stats_file)

def paper_set_warning(warning, pids):
    pids = list(pids)
    pids.sort()
    pids = '\n'.join(pids)
    print(warning)
    print(pids)

def check_pids(all_pids, reviews):
    rev_pids = set(reviews.keys())
    pap_pids = set(all_pids)
    diff = pap_pids - rev_pids
    if len(diff):
        paper_set_warning('Warning! Papers with no reviews: ', diff)
    diff = rev_pids - pap_pids
    if len(diff):
        paper_set_warning('Warning! Reviews for unrecognized papers: ', diff)

USE = 'python chair.py [papers.csv|https://papers] [reviews.csv|https://reviews] [chair.csv] [stats.csv] [--ave-all]'

def parse_args():
    ok = True
    ave_all = False
    papers_file = 'data/papers.csv'
    reviews_file = 'data/reviews.csv'
    chair_file = 'data/chair.csv'
    stats_file = 'data/stats.csv'
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print(USE)
            ok = False
        else:
            papers_file = sys.argv[1]
    if len(sys.argv) > 2:
        reviews_file = sys.argv[2]
    if len(sys.argv) > 3:
        chair_file = sys.argv[3]
    if len(sys.argv) > 4:
        stats_file = sys.argv[4]
    if len(sys.argv) > 5:
        ave_all = True
    return ok, ave_all, papers_file, reviews_file, chair_file, stats_file

def report_array(arr, name):
    print(f'{name} has {len(arr)} entries, starting:')
    print(arr[:10])

def report_dict(dict, name):
    print(f'{name} has {len(dict)} entries, starting:')
    keys = list(dict.keys())
    keys = keys[:10]
    for key in keys:
        print(dict[key])

def main():
    global verbose
    ok, ave_all, papers_file, reviews_file, chair_file, stats_file = parse_args()
    if not ok:
        return
    all_pids, dual_pids = read_papers(papers_file)
    reviews = read_reviews(reviews_file)
    if verbose:
        report_array(all_pids, 'all_pids')
        report_array(dual_pids, 'dual_pids')
        report_dict(reviews, 'reviews')
    write_outputs(all_pids, dual_pids, reviews, ave_all, chair_file, stats_file)
    check_pids(all_pids, reviews)

if __name__ == "__main__":
    main()
