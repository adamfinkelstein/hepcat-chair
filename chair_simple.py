import csv
import argparse

'''
Reads a file that looks like this:
* reviews.csv: Submission ID,Role,Score,Conf/Journal Rec,Expertise,Final Recommendation,Top 10%

Writes a file that looks like this:
* chair.csv: Submission ID,Sort Score,Status,Reviews
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

def get_parts_from_review(rev_tuple):
    role, score, final_rec = rev_tuple
    return role, score, final_rec

def get_role_from_review(rev_tuple):
    role, _, _ = get_parts_from_review(rev_tuple)
    return role

def get_score_from_review(rev_tuple):
    _, score, _ = get_parts_from_review(rev_tuple)
    return score

def get_rec_from_review(rev_tuple):
    _, _, rec = get_parts_from_review(rev_tuple)
    return rec

def get_rec_from_reviews_by_role(reviews, target_role):
    for rev_tuple in reviews:
        role, _, rec = get_parts_from_review(rev_tuple)
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
    final_rec = format_status(row[5])
    # ignore these fields for now:
    # conf_jour = to_int(row[3])
    # expertise = to_int(row[4])
    # top_10 = to_int(row[6])
    rev_tuple = (role, score, final_rec)
    return pid, rev_tuple

def read_reviews(reviews_file):
    reviews = {}
    rows = read_csv(reviews_file)
    for row in rows:
        pid, rev_tuple = row_to_pid_rev(row)
        if pid not in reviews:
            reviews[pid] = []
        reviews[pid].append(rev_tuple)
    pids = sorted(reviews.keys())
    return pids, reviews

def get_status_from_pri_sec(pid_revs):
    status = 'Tabled'
    pri = get_rec_from_reviews_by_role(pid_revs, 1)
    sec = get_rec_from_reviews_by_role(pid_revs, 2)
    if pri and sec and pri == sec:
        return pri
    return status

# note that R! and A! will be made bold in the GUI
score_codes = { -5: 'R!', -3: 'R', -1: 'r', 1: 'a', 3: 'A', 5: 'A!'}

def format_score_codes(s):
    if s in score_codes:
        return score_codes[s]
    return '?'

def format_score_list(scores):
    scores = [ format_score_codes(s) for s in scores]
    scores = ', '.join(scores)
    scores = f'[{scores}]'
    return scores

def scores_ave(scores):
    ave = sum(scores) / len(scores)
    ave = round(ave, 3)
    return ave

# output: Submission ID,Sort Score,Status,Reviews
def format_pid_with_reviews(pid, revs):
    revs.sort(key=lambda row: row[0]) # sort by role (first column)
    status = get_status_from_pri_sec(revs)
    scores = [get_score_from_review(rev) for rev in revs]
    ave = scores_ave(scores)
    reviews = format_score_list(scores)
    line = f'{pid},{ave},{status},"{reviews}"\n'
    return line

def write_file(fname, contents):
    path = f'{fname}'
    with open(path, 'w') as f:
        f.write(contents)

def write_chair(all_pids, reviews, chair_file):
    lines = 'Submission ID,Sort Score,Status,Reviews\n'
    for pid in all_pids:
        pid_revs = reviews[pid]
        lines += format_pid_with_reviews(pid, pid_revs)
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
    parser.add_argument('--reviews', default='reviews.csv',
                        help='filename of input reviews CSV')
    parser.add_argument('--chair', default='chair.csv',
                        help='filename of output chair CSV')
    args = parser.parse_args()

    verbose = args.verbose
    reviews_file = f'{args.dir}/{args.reviews}'
    chair_file = f'{args.dir}/{args.chair}'
    return reviews_file, chair_file

def main():
    global verbose
    reviews_file, chair_file = parse_args()
    all_pids, reviews = read_reviews(reviews_file)
    if verbose:
        report_array(all_pids, 'all_pids')
        report_dict(reviews, 'reviews')
    write_chair(all_pids, reviews, chair_file)

if __name__ == "__main__":
    main()
