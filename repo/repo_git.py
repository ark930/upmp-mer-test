# coding: utf-8

import os

from git import *


class GitProgress(RemoteProgress):
    """
    Git进度回调显示
    """

    def line_dropped(self, line):
        print(line)

    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, message)


class RepoGit():
    def __init__(self):
        self.local_repo_path = "../data/upmp-mer-files"
        self.remote_repo_path = "root@121.199.36.178:/var/www/upmp-test/upmp-mer-test/data/upmp-mer-files.git"
        self.repo = None

        if not os.path.exists(self.local_repo_path):
            os.mkdir(self.local_repo_path)

        if not os.path.exists(self.local_repo_path + "/.git"):
            self._clone()

        if self.repo is None:
            self.repo = Repo(self.local_repo_path)

    def _clone(self):
        self.repo = Repo.clone_from(self.remote_repo_path, self.local_repo_path, GitProgress())

    def add(self, file_name):
        if self.repo is not None:
            self.repo.git.add(file_name)

    def commit(self, comment):
        if self.repo is not None:
            self.repo.git.commit("-m " + comment)

    def pull(self, progress=None):
        if self.repo is not None:
            self.repo.git.pull(None, progress)

    def push(self):
        if self.repo is not None:
            self.repo.git.push()

    def status(self):
        if self.repo is not None:
            print(self.repo.git.status())


if __name__ == "__main__":
    gm = RepoGit()
    # gm.add("test.1")
    # gm.commit("first commit")
    # gm.pull()
    gm.status()
