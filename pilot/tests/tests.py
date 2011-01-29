# encoding: utf-8
from unittest import TestCase, TestLoader, TestSuite
from caps.pilot.tests.fixity_test import FixityTest
from caps.pilot.tests.identity_test import IdentityTest
from caps.pilot.tests.storage_test import StorageTest
from caps.pilot.tests.versioning_test import VersioningTest
from caps.pilot.tests.annotate_test import AnnotateTest


def suite():
    fixity_suite = TestLoader().loadTestsFromTestCase(FixityTest)
    identity_suite = TestLoader().loadTestsFromTestCase(IdentityTest)
    storage_suite = TestLoader().loadTestsFromTestCase(StorageTest)
    versioning_suite = TestLoader().loadTestsFromTestCase(VersioningTest)
    annotate_suite = TestLoader().loadTestsFromTestCase(AnnotateTest)
    alltests = TestSuite([fixity_suite, identity_suite, storage_suite,
                          versioning_suite, annotate_suite])
    
    return alltests
