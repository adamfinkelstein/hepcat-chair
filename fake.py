import os
import math
# import statistics
import random
import argparse
import numpy as np
from faker import Faker
# from datetime import datetime, timedelta

# globals
FAKER = Faker()
DATA_DIR = None  # global, set by command line option (default "data")


def setup_data_dir(dir):
    DATA_DIR = dir
    # make data directory if needed
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)



"""
Updated for 2025:
* users.csv: Email,First Name,Last Name,Rooms,Role,Password
* papers.csv: Submission ID,Exception,Thumbnail URL,Title,Area,Track,Room,Abstract
* clusters.csv: Submission ID,Cluster
* conflicts.csv: Submission ID,Email
* reviews.csv: Submission ID,Role,Score,Conf/Journal Rec,Expertise,Final Recommendation,Top 10%
(chair file is generated from reviews by separate program)
"""


def write_file(fname, contents):
    path = f"{DATA_DIR}/{fname}"
    with open(path, "w") as f:
        f.write(contents)


def line_to_email(line):
    parts = line.split(",")
    return parts[0]


def read_and_copy_users_file(path, fname):
    with open(path, "r") as f:
        contents = f.read()
        f.seek(0)  # rewind
        lines = f.readlines()
    write_file(fname, contents)
    lines = lines[1:]  # skip the header
    emails = [line_to_email(line) for line in lines if "," in line]
    return emails


def name_to_email(first, last):
    first = first.lower()
    last = last.lower()
    email = f"{first}.{last}@example.com"
    return email


def random_role():
    r = random.randint(0, 100)
    if r > 10:
        return ""
    elif r > 6:
        return "Chair"
    else:
        return "Admin"


paper_room_options = "1A,1B,2A,2B".split(",")
people_room_options = "1A 2A,1A 2B,1B 2A,1B 2B".split(",")


def random_paper_room():
    return random.choice(paper_room_options)


def random_user_room_codes():
    rooms = random.choice(people_room_options)
    rooms = rooms.split()  # whitespace
    return rooms


def room_code_to_room(room_code):
    return f"Room_{room_code}"


def rand_person_rooms():
    rooms = random_user_room_codes()
    rooms = [room_code_to_room(r) for r in rooms]
    rooms = ";".join(rooms)
    return rooms


# users: Email,First Name,Last Name,Rooms,Role,Password
def fake_person(role=None, first=None, last=None):
    if not first:
        first = FAKER.first_name()
    if not last:
        last = FAKER.last_name()
    if not role:
        role = ""  # formerly: random_role()
    email = name_to_email(first, last)
    rooms = rand_person_rooms()
    passwd = "" # no longer set here
    result = f"{email},{first},{last},{rooms},{role},{passwd}\n"
    return result, email


# users: Email,First Name,Last Name,Rooms,Role,Password
def fake_users(n, fname):
    emails = []
    people = "Email,First Name,Last Name,Rooms,Role,Password\n"
    person, _ = fake_person("Admin", "Fake", "Admin")
    people += person
    person, email = fake_person("Chair", "Fake", "Chair")
    people += person
    emails.append(email)
    person, email = fake_person(None, "Fake", "Citizen")
    people += person
    emails.append(email)
    while len(emails) < n:
        person, email = fake_person()
        if email in emails:
            continue # avoid duplicates
        people += person
        emails.append(email)
    write_file(fname, people)
    return emails


# def write_people_rooms(emails, fname):
#     lines = "Email,Room\n"
#     for e in emails:
#         rooms = random_user_room_codes()  # list of room codes
#         for room in rooms:
#             lines += f"{e},Room_{room}\n"
#     write_file(fname, lines)


def rand_color():
    color = "%03x" % random.randint(0, 0xFFF)
    return color


def csv_safe_string(s):
    return s.replace(",", "").replace('"', "").replace("'", "")


area_options = [
    "Animation/Simulation",
    "Imaging/Video",
    "Interaction/VR",
    "Modeling/Geometry",
    "Rendering/Visualization",
]


def fake_area():
    return random.choice(area_options)


# papers: Submission ID,Exception,Thumbnail URL,Title,Area,Track,Room,Abstract
# assumes n is a 3-digit number
def fake_paper(pid):
    c1 = rand_color()
    c2 = rand_color()
    n = pid.replace("papers_", "")
    # like this: https://fakeimg.pl/600x450/a42/fa8/?text=255&font_size=240&font=bebas
    url = f"https://fakeimg.pl/600x450/{c1}/{c2}/?text={n}&font_size=240&font=bebas"
    title = csv_safe_string(FAKER.sentence(nb_words=7))
    abstract = csv_safe_string(FAKER.paragraph(nb_sentences=12))
    title = title[:-1]  # remove trailing period
    title = title.title()  # each word caps
    area = fake_area()
    room = random_paper_room()
    track = random.choice(["Dual Track", "Journal Only Track"])
    result = f"{pid},,{url},{title},{area},{track},Room_{room},{abstract}\n"
    return result, track, room


# Submission ID,Exception,Thumbnail URL,Title,Area,Track,Room,Abstract
def fake_papers(n, fname):
    paper_rooms = {}
    dual_pids = []
    pids = []
    papers = "Submission ID,Exception,Thumbnail URL,Title,Area,Track,Room,Abstract\n"
    start = 101
    for i in range(start, start + n):
        pid = f"papers_{i}"
        paper_line, track, room = fake_paper(pid)
        paper_rooms[pid] = room
        if i == start:
            paper_line = paper_line.replace(",,http", ",Withdrawn,http")
        papers += paper_line
        pids.append(pid)
        if track == "Dual Track":
            dual_pids.append(pid)
    write_file(fname, papers)
    return pids, dual_pids, paper_rooms


def rand_num_conflicts():
    n = math.floor(np.random.poisson(3))
    return n


def rand_conflicts(emails, n):
    ems = emails.copy()
    random.shuffle(ems)
    ems = ems[:n]
    return ems


# conflicts: Submission ID,Email
def fake_conflicts(emails, papers, fname):
    conflicts = "Submission ID,Email\n"
    for pid in papers:
        n = rand_num_conflicts()
        conf = rand_conflicts(emails, n)
        for c in conf:
            conflicts += f"{pid},{c}\n"
    write_file(fname, conflicts)


def gaussian_noise(mu, sigma):
    return np.random.normal(mu, sigma)

def eval_gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.0) / (2 * np.power(sig, 2.0)))


def dumpOptions(weights, revs):
    w = np.array(weights)
    w *= 100.0 / sum(weights)
    w = np.around(w)
    w = np.uint32(w).tolist()
    print(w)
    print(revs)
    print()


def rand_reviews(n):
    # makes a weighted random choice among score options
    # mu is the mean of the gaussian, shifting the weights.
    mu = random.uniform(-3.25, 2.75) # bias towards more below bar (0.5)
    sig = 2.0
    options = [-5, -3, -1, 1, 3, 5]
    weights = []
    for opt in options:
        w = eval_gaussian(opt, mu, sig)
        weights.append(w)
    revs = random.choices(options, weights, k=n)
    return revs


def revs_to_rec_num(revs):
    noise = gaussian_noise(0, 1.5)
    ave = 1.0 * sum(revs) / len(revs) + noise
    if ave > 2:
        return 2
    elif ave > 1:
        return 1
    elif ave < -1:
        return -1
    else:
        return 0


def rec_num_to_rec(num):
    if num == 2:
        return "Journal"
    elif num == 1:
        return "Conference"
    elif num == -1:
        return "Reject"
    return "Tabled"


# 2025: Submission ID,Role,Score,Conf/Journal Rec,Expertise,Final Recommendation,Top 10%
def fmt_review(pid, role, score, conf_jour, exp, rec, top):
    line = f"{pid},{role},{score},{conf_jour},{exp},{rec},{top}\n"
    return line


def fake_paper_reviews(pid, is_dual):
    pri = "Technical Papers Committee Member (lead)"
    sec = "Technical Papers Committee Member"
    ter = "Technical Papers Tertiary Reviewer"
    ext = "Technical Papers PC Extra Reviewer"
    num_revs = random.choice([5,6])
    roles = [pri, sec, ter, ter, ter]
    if num_revs == 6:
        roles.append(random.choice([ter, ext]))
    all_scores = rand_reviews(num_revs)
    rec_num = revs_to_rec_num(all_scores)
    rec_string = rec_num_to_rec(rec_num)
    result = ""
    for i in range(num_revs):
        pri_sec_rec = rec_num if i < 2 else ""
        if is_dual:
            conf_jour = random.choice([-3,-2,-1,1,2])
        else:
            conf_jour = -3
        role = roles[i]
        score = all_scores[i]
        exp = random.randint(3, 5)
        top = 0
        if pri_sec_rec == 2 and random.randint(0, 1) == 0:
            top = 1
        result += fmt_review(pid, role, score, conf_jour, exp, pri_sec_rec, top)
    return result, rec_string, all_scores


# 2025: Submission ID,Role,Score,Conf/Journal Rec,Expertise,Final Recommendation,Top 10%
def fake_reviews(papers, dual_ids, fname):
    output = "Submission ID,Role,Score,Conf/Journal Rec,Expertise,Final Recommendation,Top 10%\n"
    recs = {}
    all_revs = {}
    for pid in papers:
        is_dual = pid in dual_ids
        lines, rec, revs = fake_paper_reviews(pid, is_dual)
        output += lines
        recs[pid] = rec
        all_revs[pid] = revs
    write_file(fname, output)
    return recs, all_revs


def all_revs_to_list(all_revs):
    arr = []
    for pid in all_revs:
        arr += all_revs[pid]
    return arr


# summary: Submission ID,Committee Notes
def fake_summaries(papers, fname):
    output = "Submission ID,Committee Notes\n"
    for pid in papers:
        summary = csv_safe_string(FAKER.sentence(nb_words=12))
        line = f"{pid},{summary}\n"
        output += line
    write_file(fname, output)


cluster_options = [*"abcde"]


# clusters: Submission ID,Type,Label
def fake_clusters(papers, fname):
    output = "Submission ID,Cluster\n"
    copy = papers[:]  # shallow copy
    keep = int(len(papers) * 0.1)  # keep 0%
    copy = copy[:keep]
    random.shuffle(copy)
    for pid in copy:
        cluster = random.choice(cluster_options)
        line = f"{pid},{cluster}\n"
        output += line
    write_file(fname, output)

def possibly_flip_status(status):
    coin = random.randint(0, 9) # 10% chance
    if coin > 0:
        return status
    # flip it
    if status == "Tabled":
        return random.choice(["Conference", "Journal","Reject"])
    return "Tabled"

# history: Submission ID,When,Context,Status
def fake_history(paper_rooms, recs, fname):
    papers = recs.keys()
    papers = list(papers)
    random.shuffle(papers)
    keep = int(len(papers) * 0.7)  # keep 70%
    papers = papers[:keep]
    copy = papers[:]  # shallow copy
    random.shuffle(copy)
    keep = int(len(papers) * 0.4)  # keep 40%
    copy = copy[:keep]
    papers += copy
    lines = []
    # now = datetime.now()
    # minus_seconds = 3600 * 24 * 7  # a week ago
    for pid in papers:
        context_options = ["Sticky", "Plenary"]
        room = paper_rooms[pid]
        if room != "P":
            room = f"Room_{room}"
            context_options.append(room)
        # minus_seconds -= random.randrange(100, 200)
        # then = now - timedelta(seconds=minus_seconds)
        # then_str = str(then)
        then_str = "2025-01-01 00:00:00"
        status = recs[pid]
        status = possibly_flip_status(status)
        context = random.choice(context_options)
        line = f"{pid},{then_str},{context},{status}\n"
        lines.append(line)
    output = "Submission ID,When,Context,Status\n"
    output += "".join(lines)
    write_file(fname, output)


def parse_args():
    global VERBOSE, DATA_DIR
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--dir', default='data',
                        help='directory for input/output CSVs')
    parser.add_argument('--users', default='',
                        help='filename of output users CSV (optional)')
    parser.add_argument('--num_users', type=int, default=50,
                        help='filename of output users CSV')
    parser.add_argument('--num_papers', type=int, default=200,
                        help='filename of output users CSV')
    args = parser.parse_args()

    VERBOSE = args.verbose
    DATA_DIR = args.dir
    users_file = args.users
    if users_file:
        users_file = f'{DATA_DIR}/{args.users}'
    return users_file, args.num_users, args.num_papers

def main():
    users_file, n_users, n_papers = parse_args()
    setup_data_dir(DATA_DIR)
    if users_file:
        emails = read_and_copy_users_file(users_file, "users.csv")
        n_users = len(emails)
    else:
        emails = fake_users(n_users, "users.csv")
    print(
        f"write data for {n_users} users and {n_papers} papers in {DATA_DIR}..."
    )
    papers, dual_pids,paper_rooms = fake_papers(n_papers, "papers.csv")
    fake_conflicts(emails, papers, "conflicts.csv")
    recs, _ = fake_reviews(papers, dual_pids, "reviews.csv")
    fake_clusters(papers, "clusters.csv")
    fake_history(paper_rooms, recs, "history.csv")


if __name__ == "__main__":
    main()
