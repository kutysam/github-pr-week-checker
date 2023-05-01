import os
from datetime import datetime, timedelta

import requests

headers = {"Authorization": f"token {os.getenv('GH_API_KEY')}"}
org_name = os.getenv("GH_ORG_NAME")
url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100"
response = requests.get(url, headers=headers)
repos = response.json()
print(len(repos))
user_url = f"https://api.github.com/orgs/{org_name}/members?per_page=100"

no_of_weeks = 4
user_response = requests.get(user_url, headers=headers).json()

from collections import defaultdict

users = defaultdict(list)
for user in user_response:
    for x in range(0, no_of_weeks + 1):
        users[user["login"]].append(0)


def append_missing_users(username):
    for x in range(0, no_of_weeks + 1):
        users[username].append(0)


def check_week(pr_date):
    for i in range(no_of_weeks):
        if pr_date > datetime.utcnow() - timedelta(
            days=((i + 1) * 7)
        ) and pr_date < datetime.utcnow() - timedelta(days=i * 7):
            return i

    print(
        f"{i} {pr_date} | {datetime.utcnow() - timedelta(days=((i + 1) * 7))} | {datetime.utcnow() - timedelta(days=i * 7)}"
    )
    return "x"


def week_print():
    wkprint = []
    for i in range(no_of_weeks):
        wkprint.append(
            f"{(datetime.utcnow() - timedelta(days=(i+1) * 7)).date()} to {(datetime.utcnow() - timedelta(days=i * 7)).date()}"
        )
    print(f',{",".join(wkprint)},total,average')


week_ago = datetime.utcnow() - timedelta(days=no_of_weeks * 7)
pull_requests = []
for repo in repos:
    print(repo["name"])
    page = 1
    END_OF_PAGE = False
    while True:
        url = f'https://api.github.com/repos/{org_name}/{repo["name"]}/pulls?per_page=100&state=all&direction=desc&page={page}'
        response = requests.get(url, headers=headers)
        prs = response.json()
        if not prs:
            break
        for pr in prs:
            if datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ") > week_ago:
                week = check_week(
                    datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                )
                username = pr["user"]["login"]
                
                try:
                    users[username][week] = users[username][week] + 1

                except IndexError:
                    append_missing_users(username)
                    users[username][week] = users[username][week] + 1

            else:
                END_OF_PAGE = True
                break
        if END_OF_PAGE:
            break
        page += 1

week_print()

for user in users.items():
    total = 0
    user[1].pop()
    for t in user[1]:
        total = total + t
    avg = total / no_of_weeks
    print(f'{user[0]},{",".join(str(v) for v in user[1])},{total},{avg}')
