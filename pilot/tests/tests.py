# encoding: utf-8
from unittest import TestCase, TestLoader, TestSuite
from caps.pilot.tests.services_test import ServicesTest


def suite():
    services_suite = TestLoader().loadTestsFromTestCase(ServicesTest)
    alltests = TestSuite([services_suite])
    
    return alltests
