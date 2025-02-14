import csv
import argparse

'''
Reads a pair of files that look like this:
* papers.csv: Submission ID,Exception,Thumbnail URL,Title,Area,Track,Room,Abstract
* reviews.csv: Submission ID,Role,Score,Conf/Journal Rec,Expertise,Final Recommendation,Top 10%

Writes a file that looks like this:
* chair.csv: Submission ID,Sort Score,Status,Reviews

Relies on notes on review scores from Mark L Feb 2025:

Score
-5 // Strong reject
-3 // Reject
-1 // Borderline reject
1 // Borderline accept
3 // Accept
5 // Strong accept

Conf/Journal Rec
-3// Not suitable for either
-2// Better suited for conference, if the paper is accepted
-1// Borderline conference, if the paper is accepted
1// Borderline journal, if the paper is accepted
2// Better suited for journal, if the paper is accepted

Expertise
3 // Novice
4 // Intermediate 
5 // Expert

Final Recommendation
-1 // Reject
0 // Table
1 // Conference Accept
2 // Journal Accept

Top 5%
0 // No
1 // Yes
'''

# globals
verbose = False

def read_csv_rows(reader):
    rows = []
    skip_header = True
    for row in reader:
        if skip_header:
            skip_header = False
            continue
        rows.append(row)
    return rows

def read_csv(fname):
    with open(fname, 'r') as f:
        reader = csv.reader(f)
        rows = read_csv_rows(reader)
        return rows


# papers.csv: Submission ID,Exception,Thumbnail URL,Title,Area,Track,Room,Abstract
# pull out: IDs, Exceptions, Tracks
# track is either: "Dual Track" or "Journal Only Track"
def read_papers(papers_file):
    all_pids = []
    dual_pids = []
    exceptions = {}
    rows = read_csv(papers_file)
    for row in rows:
        pid = row[0]
        exception = row[1]
        track = row[5]
        all_pids.append(pid)
        if track == 'Dual Track':
            dual_pids.append(pid)
        if exception:
            exceptions[pid] = exception
    return all_pids, dual_pids, exceptions


'''
known options:
Technical Papers Committee Member (lead)
Technical Papers Committee Member
Technical Papers Tertiary Reviewer
Technical Papers PC Extra Reviewer
'''
def get_role_number_from_role(role):
    if 'lead' in role:
        return 1
    if 'Member' in role:
        return 2
    if 'Tertiary' in role:
        return 3
    if 'Extra' in role:
        return 4
    return 5

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

def get_part_from_review(rev_tuple, index):
    return rev_tuple[index]

def get_role_from_review(rev_tuple):
    return get_part_from_review(rev_tuple, 0)

def get_score_from_review(rev_tuple):
    return get_part_from_review(rev_tuple, 1)

def get_rec_from_review(rev_tuple):
    return get_part_from_review(rev_tuple, 2)

def get_conf_from_review(rev_tuple):
    return get_part_from_review(rev_tuple, 3)

def get_rec_from_reviews_by_role(reviews, target_role):
    for rev_tuple in reviews:
        role = get_role_from_review(rev_tuple)
        rec = get_rec_from_review(rev_tuple)
        if role == target_role:
            return rec
    return None

# 2025: Submission ID,Role,Score,Conf/Journal Rec,Expertise,Final Recommendation,Top 10%
# 0: Submission ID
# 1: Role
# 2: Score
# 3: Conf/Journal Rec
# 4: Expertise
# 5: Final Recommendation
# 6: Top 10%
def row_to_pid_rev(row):
    pid = row[0]
    role = get_role_number_from_role(row[1])
    score = to_int(row[2])
    conf_jour = to_int(row[3])
    final_rec = format_status(row[5])
    # ignore these fields for now:
    # expertise = to_int(row[4])
    # top_10 = to_int(row[6])
    rev_tuple = (role, score, final_rec, conf_jour)
    return pid, rev_tuple

def read_reviews(all_pids, reviews_file):
    reviews = {}
    rows = read_csv(reviews_file)
    for row in rows:
        pid, rev_tuple = row_to_pid_rev(row)
        if pid not in all_pids:
            continue # ignore reviews for papers not in the papers file
        if pid not in reviews:
            reviews[pid] = []
        reviews[pid].append(rev_tuple)
    return reviews

def get_status_from_pri_sec(pid_revs):
    status = 'Tabled'
    pri = get_rec_from_reviews_by_role(pid_revs, 1)
    sec = get_rec_from_reviews_by_role(pid_revs, 2)
    if pri and sec and pri == sec:
        return pri
    return status

# note that R! and A! will be made bold in the GUI
score_codes = { -5: 'R!', -3: 'R', -1: 'r', 1: 'a', 3: 'A', 5: 'A!'}

conf_jour_codes = { -3: 'x', -2: 'C', -1: 'c', 1: 'j', 2: 'J'}

def format_score_codes(s):
    if s in score_codes:
        return score_codes[s]
    return '?'

def format_conf_jour_codes(c):
    if c in conf_jour_codes:
        return conf_jour_codes[c]
    return '?'

def format_score_list(scores):
    scores = [ format_score_codes(s) for s in scores]
    scores = ', '.join(scores)
    scores = f'[{scores}]'
    return scores

def format_conf_jour_list(codes):
    codes = [ format_conf_jour_codes(c) for c in codes]
    codes = ', '.join(codes)
    codes = f'({codes})'
    return codes

def scores_ave(scores):
    ave = sum(scores) / len(scores)
    ave = round(ave, 3)
    return ave

# output: Submission ID,Sort Score,Status,Reviews
def format_pid_with_reviews(pid, is_dual, revs):
    revs.sort(key=lambda row: row[0]) # sort by role (first column)
    status = get_status_from_pri_sec(revs)
    scores = [get_score_from_review(rev) for rev in revs]
    ave = scores_ave(scores)
    scores = format_score_list(scores)
    if is_dual:
        conf_jour = [get_conf_from_review(rev) for rev in revs]
        conf_jour = format_conf_jour_list(conf_jour)
    else:
        conf_jour = '(J only)'
    line = f'{pid},{ave},{status},"{conf_jour} {scores}"\n'
    return line

def format_pid_with_exception(pid, exception):
    line = f'{pid},-6,Reject,"Exception: {exception}"\n'
    return line

def format_pid_with_no_reviews(pid):
    line = f'{pid},-5,Tabled,"(Missing reviews!)"\n'    
    return line

def write_file(fname, contents):
    path = f'{fname}'
    with open(path, 'w') as f:
        f.write(contents)

def write_chair(all_pids, dual_pids, exceptions, reviews, chair_file):
    lines = 'Submission ID,Sort Score,Status,Reviews\n'
    for pid in all_pids:
        if pid in exceptions:
            exception = exceptions[pid]
            lines += format_pid_with_exception(pid, exception)
        elif pid in reviews:
            pid_revs = reviews[pid]
            is_dual = pid in dual_pids
            lines += format_pid_with_reviews(pid, is_dual, pid_revs)
        else:
            lines += format_pid_with_no_reviews(pid)
    write_file(chair_file,lines)

def report_array(arr, name):
    print(f'{name} has {len(arr)} entries, starting:')
    print(arr[:10])

def report_dict(dict, name):
    print(f'{name} has {len(dict)} entries, starting:')
    keys = list(dict.keys())
    keys = keys[:10]
    for key in keys:
        print(dict[key])

def parse_args():
    global verbose
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--dir', default='data',
                        help='directory for input/output CSVs')
    parser.add_argument('--papers', default='papers.csv',
                        help='filename of input papers CSV')
    parser.add_argument('--reviews', default='reviews.csv',
                        help='filename of input reviews CSV')
    parser.add_argument('--chair', default='chair.csv',
                        help='filename of output chair CSV')
    args = parser.parse_args()

    verbose = args.verbose
    papers_file = f'{args.dir}/{args.papers}'
    reviews_file = f'{args.dir}/{args.reviews}'
    chair_file = f'{args.dir}/{args.chair}'
    return papers_file, reviews_file, chair_file

def main():
    global verbose
    papers_file, reviews_file, chair_file = parse_args()
    all_pids, dual_pids, exceptions = read_papers(papers_file)
    reviews = read_reviews(all_pids, reviews_file)
    if verbose:
        report_array(all_pids, 'all_pids')
        report_dict(reviews, 'reviews')
        report_dict(exceptions, 'exceptions')
    write_chair(all_pids, dual_pids, exceptions, reviews, chair_file)

if __name__ == "__main__":
    main()
