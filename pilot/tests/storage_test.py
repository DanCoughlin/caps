# encoding: utf-8
import os
import glob
import shutil
import tempfile
from django.test import TestCase
from caps.services import identity, storage


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
  
class StorageTest(TestCase):
    # fixtures = ['test_data.json']
    
    def setUp(self):
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

    def tearDown(self):
        # clean up all the test dirs
        shutil.rmtree(self.repodir)
        shutil.rmtree(self.bagdir)

    def do_something_with_storage(self):
        self.assertTrue(True)

