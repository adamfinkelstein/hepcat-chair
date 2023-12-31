import os
import sys
import math
import statistics
import random
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

# globals
FAKER = Faker()
DATA_DIR = "data"  # global, may be changed by command line option


def setup_data_dir(dir):
    DATA_DIR = dir
    # make data directory if needed
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


# users: Email,First Name,Last Name,Role,Password
# people_rooms: Email,Rooms
# papers: Submission ID,Thumbnail URL,Title,Area,Dual Track,Abstract
# paper_rooms: Submission ID,Room
# conflicts: Submission ID,Email
# clusters: Submission ID,Cluster
# reviews: Submission ID,Role,Conference Score,Journal Score,Expertise,Final Recommendation
# summaries: Submission ID,Committee Notes
# history: Submission ID,When,Context,Status

"""
__SA23__ files from linklings have these headers:
users: Email,First Name,Last Name,Admin,Password
papers: Submission ID,Thumbnail URL,Title,Area,Dual Track,Abstract
conflicts: Submission ID,Email
clusters: Submission ID,Cluster
reviews: Submission ID,Role,Conference Score,Journal Score,Expertise (*)
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


paper_room_options = [*"ABXYP"]
people_room_options = "AX,BY,BX,BY".split(",")


def random_paper_room():
    return random.choice(paper_room_options)


def random_people_rooms():
    return random.choice(people_room_options)


# users: Email,First Name,Last Name,Role,Password
def fake_person(default_password, role=None, first=None, last=None):
    if not first:
        first = FAKER.first_name()
    if not last:
        last = FAKER.last_name()
    if not role:
        role = ""  # formerly: random_role()
    email = name_to_email(first, last)
    if default_password:
        passwd = default_password
    else:
        passwd = FAKER.password()
    result = f"{email},{first},{last},{role},{passwd}\n"
    return result, email


def fake_users(n, default_password, fname):
    emails = []
    people = "Email,First Name,Last Name,Role,Password\n"
    person, _ = fake_person(default_password, "Admin")
    people += person
    person, email = fake_person(default_password, "Screen", "Screen", "User")
    people += person
    emails.append(email)
    for _ in range(2, n):
        person, email = fake_person(default_password, None)
        people += person
        emails.append(email)
    write_file(fname, people)
    return emails


def write_people_rooms(emails, fname):
    lines = "Email,Rooms\n"
    for e in emails:
        rooms = random_people_rooms()
        lines += f"{e},{rooms}\n"
    write_file(fname, lines)


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


# papers: Submission ID,Thumbnail URL,Title,Area,Conference,Abstract
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
    dual = random.choice(["yes", "no"])
    result = f"{pid},{url},{title},{area},{dual},{abstract}\n"
    return result, dual


def fake_papers(n, fname):
    dual_pids = []
    pids = []
    papers = "Submission ID,Thumbnail URL,Title,Area,Dual Track,Abstract\n"
    start = 101
    for i in range(start, start + n):
        pid = f"papers_{i}"
        paper_line, dual = fake_paper(pid)
        papers += paper_line
        pids.append(pid)
        if dual == "yes":
            dual_pids.append(pid)
    write_file(fname, papers)
    return pids, dual_pids


def write_paper_rooms(pids, fname):
    paper_rooms = {}
    lines = "Submission ID,Room\n"
    for p in pids:
        room = random_paper_room()
        paper_rooms[p] = room
        lines += f"{p},{room}\n"
    write_file(fname, lines)
    return paper_rooms


def rand_num_conflicts():
    n = math.floor(np.random.poisson(3))
    return n


def filter_emails_without_screen(emails):
    return [email for email in emails if not "screen" in email]


def rand_conflicts(emails, n):
    # ems = emails.copy()
    ems = filter_emails_without_screen(emails)
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


def gaussian(x, mu, sig):
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
    mu = random.uniform(-3.0, 3.0)
    sig = 2.0
    options = [-5, -3, -1, 1, 3, 5]
    weights = []
    for opt in options:
        w = gaussian(opt, mu, sig)
        weights.append(w)
    revs = random.choices(options, weights, k=n)
    # dumpOptions(weights, revs)
    # if random.uniform(0.0,1.0) > 0.5:
    #     for i in range(5):
    #         revs[i] = 0
    return revs


def review_score_to_dual_rec(score):
    if score == 5:
        return 2
    elif score == 3:
        return random.choice([1, -1])
    elif score == 1:
        return -2
    return -3


def revs_to_rec(revs):
    tot = 1.0 * sum(revs) / len(revs)
    if tot > 1.6:
        return 1
    elif tot < -1:
        return -1
    else:
        return 0


def gen_status(rec):
    if rec == 0:
        return "0", "Tabled"
    if rec > 0:
        coin = bool(random.getrandbits(1))
        if coin:
            return "1", "Conference"
        else:
            return "2", "Journal"
    return "-1", "Reject"


# 2022: Submission ID,Role,Conference Score,Journal Score,Expertise,Final Recommendation
# 2023: Submission ID,Role,Score,Conf/Jounal Rec,Expertise,Final Recommendation,Top 10%
# Expertise and Top 10 ignored for now in Hepcat
# sa22: Submission ID,Role,Conference Score,Journal Score,Expertise,Final Recommendation
def fmt_review(pid, role, conf, jour, rec):
    line = f"{pid},{role},{conf},{jour},99,{rec},\n"
    return line


def fake_paper_reviews(pid, is_dual):
    pri = "Technical Papers Committee Member (lead)"
    sec = "Technical Papers Committee Member"
    ter = "Technical Papers Tertiary Reviewer"
    roles = [pri, sec, ter, ter, ter]
    jour_revs = rand_reviews(5)
    rec, rec_string = gen_status(revs_to_rec(jour_revs))
    if is_dual:
        conf_revs = rand_reviews(5)
    else:
        conf_revs = [0, 0, 0, 0, 0]
    # print(conf, revs)
    result = ""
    for i in range(5):
        reci = rec if i < 2 else ""
        result += fmt_review(pid, roles[i], conf_revs[i], jour_revs[i], reci)
    return result, rec_string, jour_revs


# orig: Submission ID,Role,Conference Score,Journal Score,Consensus Recommendation
# 2022: Submission ID,Role,Conference Score,Journal Score,Expertise,Final Recommendation
# 2023: Submission ID,Role,Score,Conf/Jounal Rec,Expertise,Final Recommendation,Top 10%
# sa23: Submission ID,Role,Conference Score,Journal Score,Expertise,Final Recommendation
def fake_reviews(papers, dual_pids, fname):
    output = "Submission ID,Role,Conference Score,Journal Score,Expertise,Final Recommendation\n"
    recs = {}
    all_revs = {}
    for pid in papers:
        is_dual = pid in dual_pids
        lines, rec, revs = fake_paper_reviews(pid, is_dual)
        output += lines
        recs[pid] = rec
        all_revs[pid] = revs
    write_file(fname, output)
    return recs, all_revs


def mean_and_std(scores):
    n = len(scores)
    if not n:
        return 0, 1
    mean = statistics.mean(scores)
    std = statistics.stdev(scores)
    return mean, std


def all_revs_to_list(all_revs):
    arr = []
    for pid in all_revs:
        arr += all_revs[pid]
    return arr


# chair_scores: Submission ID,Chair Score
# def fake_chair_scores(all_revs, fname):
#     revs = all_revs_to_list(all_revs)
#     mu, sigma = mean_and_std(revs)
#     output = 'Submission ID,Chair Score\n'
#     for pid in all_revs:
#         revs = all_revs[pid]
#         mean,_ = mean_and_std(revs)
#         score = (mean-mu) / sigma
#         line = f'{pid},{score}\n'
#         output += line
#     write_file(fname, output)


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
    dups = papers[:]  # shallow copy
    keep = int(len(papers) * 0.1)  # keep 0%
    dups = dups[:keep]
    random.shuffle(dups)
    for pid in dups:
        cluster = random.choice(cluster_options)
        line = f"{pid},{cluster}\n"
        output += line
    write_file(fname, output)


# history: Submission ID,When,Context,Status
def fake_history(paper_rooms, recs, fname):
    papers = recs.keys()
    papers = list(papers)
    random.shuffle(papers)
    keep = int(len(papers) * 0.7)  # keep 70%
    papers = papers[:keep]
    dups = papers[:]  # shallow copy
    random.shuffle(dups)
    keep = int(len(papers) * 0.4)  # keep 40%
    dups = dups[:keep]
    papers += dups
    lines = []
    now = datetime.now()
    minus_seconds = 3600 * 24 * 7  # a week ago
    for pid in papers:
        context_options = ["Stickie", "Plenary"]
        room = paper_rooms[pid]
        if room != "P":
            room = f"Room_{room}"
            context_options.append(room)
        minus_seconds -= random.randrange(100, 200)
        then = now - timedelta(seconds=minus_seconds)
        then_str = str(then)
        status = recs[pid]
        context = random.choice(context_options)
        line = f"{pid},{then_str},{context},{status}\n"
        lines.append(line)
    output = "Submission ID,When,Context,Status\n"
    output += "".join(lines)
    write_file(fname, output)


USE = (
    "python fake.py [data_dir] [n_users|existing_users.csv] [n_papers] [default_passwd]"
)


def parse_args():
    global DATA_DIR
    ok = True
    default_password = None
    n_users = 50
    users_file = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print(USE)
            ok = False
        else:
            DATA_DIR = sys.argv[1]  # global
    if len(sys.argv) > 2:
        if sys.argv[2].isnumeric():
            n_users = int(sys.argv[2])
        else:
            n_users = 0
            users_file = sys.argv[2]
    if len(sys.argv) > 3:
        n_papers = int(sys.argv[3])
    else:
        n_papers = n_users * 10
    if len(sys.argv) > 4:
        default_password = sys.argv[4]
    return ok, users_file, n_users, n_papers, default_password


def main():
    ok, users_file, n_users, n_papers, default_password = parse_args()
    if not ok:
        return
    setup_data_dir(DATA_DIR)
    if users_file:
        emails = read_and_copy_users_file(users_file, "users.csv")
        n_users = len(emails)
    else:
        emails = fake_users(n_users, default_password, "users.csv")
    print(
        f"writing fake data for {n_users} users and {n_papers} papers in {DATA_DIR}..."
    )
    write_people_rooms(emails, "people_rooms.csv")
    papers, dual_pids = fake_papers(n_papers, "papers.csv")
    paper_rooms = write_paper_rooms(papers, "paper_rooms.csv")
    fake_conflicts(emails, papers, "conflicts.csv")
    recs, _ = fake_reviews(papers, dual_pids, "reviews.csv")
    fake_clusters(papers, "clusters.csv")
    fake_history(paper_rooms, recs, "history.csv")
    # SA23: no longer write chair scores from this program,
    # ...and no longer use summaries.
    # fake_chair_scores(all_revs, 'chair_scores.csv')
    # fake_summaries(papers, 'summaries.csv')


if __name__ == "__main__":
    main()
