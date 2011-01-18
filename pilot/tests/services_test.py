# encoding: utf-8
import os.path
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
    
    VERSIONING

    Initiate versioning on an object (init)
    List versions of an object/file (log)
    View version history (log)
    Show diffs of an object/file (diff)
    Restore a version by date/name
    Add an untracked file (add, commit)
    Name a version (tag)
    Update a file (add, commit)
    Remove a file (rm, commit)
    Rename a file (mv, commit)

    """
    def test_init_version(self):
        self.assertTrue(False)

    def test_list_versions(self):
        self.assertTrue(False)

    def test_view_version_history(self):
        self.assertTrue(False)

    def test_view_version_diff_file(self):
        self.assertTrue(False)

    def test_view_version_diff_object(self):
        self.assertTrue(False)

    def test_restore_version_by_number(self):
        self.assertTrue(False)

    def test_restore_version_by_date(self):
        self.assertTrue(False)

    def test_add_untracked_file(self):
        self.assertTrue(False)

    def test_tag_version(self):
        self.assertTrue(False)

    def test_update_file(self):
        self.assertTrue(False)

    def test_remove_file(self):
        self.assertTrue(False)

    def test_rename_file(self):
        self.assertTrue(False)

