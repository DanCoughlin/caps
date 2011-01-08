# encoding: utf-8

import datetime
from unittest import TestCase

from django.contrib.auth.models import User
from django.core.management import call_command

#from caps.pilot.models import *
from caps.services import *

class ServicesTest (TestCase):
    
    # fixtures = ['test_data.json']
    
    def setUp(self):
        #self.test_user = User.objects.get_or_create(username='tester', password='')[0]
        self.assertTrue(True)
        
    def test_annotate(self):
        self.assertTrue(True)


