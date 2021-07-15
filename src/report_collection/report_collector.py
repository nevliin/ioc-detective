import json
import os
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List, Optional

import requests
from timeloop import Timeloop

collection_started = False


@dataclass
class ReportsInfo:
    last_checked: Optional[datetime]
    reports: List


class ReportCollector:
    data_storage_file = os.path.join(os.path.dirname(__file__), '../../data/reports.json')
    timedelta_if_new = 30  # days

    repos = []

    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), '../config.json')) as f:
            config = json.load(f)
        self.repos = config["github_repos"] if "github_repos" in config else []

        self.setup_action()

    def setup_action(self):
        tl = Timeloop()

        @tl.job(interval=timedelta(minutes=15))
        def execute():
            self.find_new_reports()

        global collection_started
        if not collection_started:
            self.find_new_reports()
            tl.start()
            collection_started = True

    def find_new_reports(self):
        if not os.path.exists(self.data_storage_file):
            since = datetime.now() - timedelta(days=self.timedelta_if_new)
            data_storage = {
                'last_checked': datetime.now().isoformat(),
                'reports': {}
            }
        else:
            with open(self.data_storage_file, 'r') as f:
                data_storage = json.load(f)

            since = datetime.fromisoformat(data_storage['last_checked'])

        try:
            for repo in self.repos:
                auth = (repo["github_authn_user"], repo["github_authn_token"])
                all_commits_url = repo['url'].rstrip('/') + '/commits?since=' + since.isoformat()
                res_commits = requests.get(all_commits_url, auth=auth)
                if res_commits.status_code == 200:
                    for commit in reversed(res_commits.json()):
                        date = commit['commit']['committer']['date'].replace('Z', '+00:00')
                        sha = commit['sha']
                        try:
                            commit_url = repo['url'].rstrip('/') + '/commits/' + sha
                            res_commit = requests.get(commit_url, auth=auth).json()
                            for file in res_commit['files']:
                                file_url: str = file['raw_url']
                                if file_url.lower().endswith('.pdf'):
                                    file_name = file_url.split('/')[-1]
                                    file_name = file_name.replace('%20', ' ')
                                    data_storage['reports'][file_name] = {
                                        'last_updated': date,
                                        'commit_sha': sha,
                                        'file_url': file_url,
                                        'source': repo['url']
                                    }
                        except Exception as e:
                            print(f'Exception occurred while querying new reports: {e}')
                            continue
                    data_storage['last_checked'] = datetime.now().isoformat()
                    with open(self.data_storage_file, 'w') as f:
                        json.dump(data_storage, f, indent=4)
                else:
                    raise ValueError('Status code is not 200')
        except Exception as e:
            print(f'Exception occurred while querying new reports: {e}')

    def get_reports(self) -> ReportsInfo:
        if not os.path.exists(self.data_storage_file):
            return ReportsInfo(last_checked=None, reports=[])
        with open(self.data_storage_file, 'r') as f:
            data_storage = json.load(f)
            reports = [{
                'url': report['file_url'],
                'name': name,
                'last_updated': datetime.fromisoformat(report['last_updated']),
                'source': report['source']
            } for name, report in data_storage['reports'].items()]

            reports = list(sorted(reports, reverse=True, key=lambda entry: entry['last_updated']))

            return ReportsInfo(last_checked=datetime.fromisoformat(data_storage['last_checked']), reports=reports)

    def remove_report(self, name: str) -> bool:
        if not os.path.exists(self.data_storage_file):
            return True
        try:
            with open(self.data_storage_file, 'r') as f:
                data_storage = json.load(f)

            del data_storage['reports'][name]

            with open(self.data_storage_file, 'w') as f:
                json.dump(data_storage, f, indent=4)
            return True
        except Exception as e:
            print(e)
            return False


ReportCollector()
