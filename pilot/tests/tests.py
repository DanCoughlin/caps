# encoding: utf-8

from unittest import TestCase, TestLoader, TestSuite
from caps.pilot.tests.services_test import ServicesTest


def suite():
    servicesSuite = TestLoader().loadTestsFromTestCase(ServicesTest)
    alltests = TestSuite([servicesSuite])
    
    return alltests
