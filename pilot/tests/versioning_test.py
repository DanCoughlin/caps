# encoding: utf-8
import os
import git
import shutil
import tempfile
from django.test import TestCase
from caps.services import storage


class VersioningTest(TestCase):
    # fixtures = ['test_data.json']
    
    def setUp(self):
        self.workdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def test_init_version(self):
        self.assertRaises(git.InvalidGitRepositoryError,
                          git.Repo,
                          self.workdir)
        repo = storage.init_version(self.workdir)
        self.assertEqual(type(repo),
                         git.repo.base.Repo)

    def test_add_one_untracked_file(self):
        repo = storage.init_version(self.workdir)
        (index, untracked) = storage.stage_all(repo)
        self.assertEqual(len(repo.untracked_files),
                         0)
        self.assertEqual(untracked,
                         repo.untracked_files)

        (h, f) = tempfile.mkstemp(dir=self.workdir)
        self.assertEqual(len(repo.untracked_files),
                         1)
        self.assertEqual(repo.untracked_files,
                         [os.path.basename(f)])
        self.assertNotEqual(untracked,
                            repo.untracked_files)

        (index, untracked) = storage.stage_all(repo)
        c = storage.commit_version(index, "qwertyuiop")
        self.assertEqual(len(repo.untracked_files),
                         0)                          
        self.assertEqual(c.message, "qwertyuiop")

    def test_add_commit_one_file_not_any_others(self):
        repo = storage.init_version(self.workdir)

        # repo and index should be empty
        (index, untracked) = storage.stage_all(repo)
        self.assertEqual(len(repo.untracked_files),
                         0)
        self.assertEqual(len(index.entries),
                         0)

        (h1, f1) = tempfile.mkstemp(dir=self.workdir)
        (h2, f2) = tempfile.mkstemp(dir=self.workdir)
        # two files should be untracked
        self.assertEqual(len(repo.untracked_files),
                         2)
        self.assertTrue(os.path.basename(f1) in repo.untracked_files)
        self.assertTrue(os.path.basename(f2) in repo.untracked_files)

        index = storage.stage_file(repo, f1)
        # f2 should be untracked; f1 in the index
        self.assertFalse(os.path.basename(f1) in repo.untracked_files)
        self.assertTrue(os.path.basename(f2) in repo.untracked_files)
        self.assertEqual(len(index.entries),
                         1)
        self.assertEqual(index.entries.keys()[0][0],
                         os.path.basename(f1))

        c = storage.commit_version(index, f1)
        # after the commit, f1 should be committed, f2 should be untracked
        # and there should be 0 files in the index
        self.assertFalse(os.path.basename(f1) in repo.untracked_files)
        self.assertTrue(os.path.basename(f2) in repo.untracked_files)
        self.assertEqual(len(index.entries),
                         0)
        self.assertEqual(len(repo.untracked_files),
                         1)
        self.assertEqual(c.message, f1)

    def test_update_file(self):
        #Update a file (add, commit)
        repo = storage.init_version(self.workdir)
        (h, f) = tempfile.mkstemp(dir=self.workdir)
        with open(f) as fh:
            fcontents = fh.read()
        self.assertEqual(fcontents, '')
        i = storage.stage_file(repo, f)
        storage.commit_version(i)
        self.assertEqual(len(i.entries), 0)
        with open(f, 'a') as fh:
            fh.write("foobar")
        with open(f) as fh:
            fcontents = fh.read()
        self.assertEqual(fcontents, 'foobar')
        i = repo.index
        self.assertEqual(len(i.entries), 1)
        storage.commit_version(i)
        self.assertEqual(len(i.entries), 0)

    def test_remove_file(self):
        #Remove a file (rm, commit)
        repo = storage.init_version(self.workdir)
        (h, f) = tempfile.mkstemp(dir=self.workdir)
        i = storage.stage_file(repo, f)
        storage.commit_version(i, message="file added")
        self.assertTrue(os.path.exists(f))
        c = storage.remove_versioned_file(repo, f, message="nuked: %s" % f)
        self.assertEqual(c.message, "nuked: %s" % f)
        self.assertFalse(os.path.exists(f))
 
    def test_rename_file(self):
        #Rename a file (mv, commit)
        repo = storage.init_version(self.workdir)
        (h, f) = tempfile.mkstemp(dir=self.workdir)
        i = storage.stage_file(repo, f)
        storage.commit_version(i, message="file added")
        f2 = os.path.join(self.workdir, "new_name")
        self.assertTrue(os.path.exists(f))
        self.assertFalse(os.path.exists(f2))
        c = storage.rename_versioned_file(repo, f, f2, message="mved: %s" % f)
        self.assertEqual(c.message, "mved: %s" % f)
        self.assertFalse(os.path.exists(f))
        self.assertTrue(os.path.exists(f2))

    def test_list_versions_object(self):
        #List versions of an object (log)
        repo = storage.init_version(self.workdir)
        (h, f) = tempfile.mkstemp(dir=self.workdir)
        i = storage.stage_file(repo, f)
        c1 = storage.commit_version(i, "first")
        with open(f, "a") as fh:
            fh.write("second")
        i = storage.stage_file(repo, f)
        c2 = storage.commit_version(i, "second")
        with open(f, "a") as fh:
            fh.write("third")
        i = storage.stage_file(repo, f)
        c3 = storage.commit_version(i, "third")
        versions = storage._list_versions(repo)
        # returns a list. each item is a dict representing a commit,
        #   with the key = commit id and the value = commit message
        latest_version = versions.pop(0)
        self.assertEqual(latest_version.keys()[0], c3.hexsha)
        self.assertEqual(latest_version.values()[0], c3.message)
        latest_version = versions.pop(0)
        self.assertEqual(latest_version.keys()[0], c2.hexsha)
        self.assertEqual(latest_version.values()[0], c2.message)
        latest_version = versions.pop(0)
        self.assertEqual(latest_version.keys()[0], c1.hexsha)
        self.assertEqual(latest_version.values()[0], c1.message)

    def test_list_versions_file(self):
        #List versions of a file (log)
        repo = storage.init_version(self.workdir)
        """
        TODO: VERSION MULTIPLE FILES, MULTIPLE COMMITS
        """
        (h, f1) = tempfile.mkstemp(dir=self.workdir)
        (h, f2) = tempfile.mkstemp(dir=self.workdir)
        print "first stage (both)"
        (i, u) = storage.stage_all(repo)
        c1 = storage.commit_version(i, "initial for both")
        with open(f1, "a") as fh:
            fh.write("first edit to f1")
        print "second stage (f1)"
        i = storage.stage_file(repo, f1)
        c2 = storage.commit_version(i, "second for f1")
        with open(f2, "a") as fh:
            fh.write("first edit to f2")
        print "third stage (f2)"
        i = storage.stage_file(repo, f2)
        c3 = storage.commit_version(i, "second for f2")
        with open(f1, "a") as fh:
            fh.write("second edit to f1")
        with open(f2, "a") as fh:
            fh.write("second edit to f2")
        print "fourth stage (both)"
        (i, u) = storage.stage_all(repo)
        c4 = storage.commit_version(i, "third for both")
        with open(f2, "a") as fh:
            fh.write("third edit to f2")
        print "fifth stage (f2)"
        i = storage.stage_file(repo, f2)
        c5 = storage.commit_version(i, "fourth for f2")
        
        f1versions = storage._list_versions(repo, f1)
        f2versions = storage._list_versions(repo, f2)
        # returns a list. each item is a dict representing a commit,
        #   with the key = commit id and the value = commit message
        self.assertEqual(len(f1versions), 3)
        self.assertEqual(len(f2versions), 4)
        latest_f1version = f1versions.pop(0)
        self.assertEqual(latest_f1version.keys()[0], c4.hexsha)
        self.assertEqual(latest_f1version.values()[0], c4.message)
        latest_f2version = f2versions.pop(0)
        self.assertEqual(latest_f2version.keys()[0], c5.hexsha)
        self.assertEqual(latest_f2version.values()[0], c5.message)
        earliest_f1version = f1versions.pop()
        self.assertEqual(earliest_f1version.keys()[0], c1.hexsha)
        self.assertEqual(earliest_f1version.values()[0], c1.message)
        earliest_f2version = f2versions.pop()
        self.assertEqual(earliest_f2version.keys()[0], c1.hexsha)
        self.assertEqual(earliest_f2version.values()[0], c1.message)

    def test_view_version_history(self):
        #View version history (log)
        self.assertTrue(True)

    def test_view_version_diff_file(self):
        #Show diffs of an file (diff)
        self.assertTrue(True)

    def test_view_version_diff_object(self):
        #Show diffs of an object (diff)
        self.assertTrue(True)

    def test_restore_version_by_number(self):
        #Restore a version by name/number (checkout?)
        self.assertTrue(True)

    def test_restore_version_by_date(self):
        #Restore a version by date (checkout?)
        self.assertTrue(True)

    def test_tag_version(self):
        #Name a version (tag)
        self.assertTrue(True)

