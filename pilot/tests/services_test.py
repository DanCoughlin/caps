# encoding: utf-8
import os
import git
import glob
import shutil
import tempfile
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
#from caps.pilot.models import *
from caps.services import identity, fixity, storage, annotate


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
  
class ServicesTest(TestCase):
    # fixtures = ['test_data.json']
    
    def setUp(self):
        """

        Should we want a complete mini-repo for tests, uncomment this block
        and the one in self.tearDown()

        # first create a temp dir for the test repo, which will be created and
        #   destroyed for *each* test method below.  This is what we delete
        #   in self.tearDown().
        self.repodir = tempfile.mkdtemp()
        # pairtree library used in storage.create_store)_ requires a directory
        #   that does not exist, and self.repodir was just created.  So we
        #   create an arbitrary dir within it for the pairtree
        self.treedir = os.path.join(self.repodir, "stewardship")
        # create a directory to hold test data to be bagged.  since the bag
        #   library makes the bag in situ, we need a new bagdir per test
        self.bagdir = tempfile.mkdtemp() 
        storage.create_store(self.treedir)
        ark = identity.mint()
        for f in glob.glob(os.path.join(DATA_DIR, "content_source", "*")):
            shutil.copy2(f, self.bagdir)
        storage.add_object(ark, self.bagdir, override_tree_location=self.treedir)

        """
        self.workdir = tempfile.mkdtemp()

    def tearDown(self):
        """

        # clean up all the test dirs
        shutil.rmtree(self.repodir)
        shutil.rmtree(self.bagdir)
        
        """
        shutil.rmtree(self.workdir)

    """

    TODO: Tests for:

    STORE
    VERIFY
    IDENTIFY
    ANNOTATE

    """
    
    """ VERSION """

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
        self.assertTrue(True)

    def test_remove_file(self):
        #Remove a file (rm, commit)
        self.assertTrue(True)
 
    def test_rename_file(self):
        #Rename a file (mv, commit)
        self.assertTrue(True)

    def test_list_versions(self):
        #List versions of an object/file (log)
        self.assertTrue(True)

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

