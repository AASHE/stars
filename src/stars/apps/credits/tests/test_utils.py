"""
    Test for get_next_variable_name
"""

from django.test import TestCase

from stars.apps.credits.models import *
from stars.apps.credits.utils import var_to_int, get_next_variable_name, int_to_var

import sys
from datetime import date

class TestUtils(TestCase):
    
    def setUp(self):
        pass

    def testIntToVar(self):
        self.assertEqual(int_to_var(0), 'A')
        self.assertEqual(int_to_var(1), 'B')
        self.assertEqual(int_to_var(2), 'C')
        self.assertEqual(int_to_var(25), 'Z')
        self.assertEqual(int_to_var(26), 'AA')
    
    def testVarToInt(self):
        self.assertEqual(var_to_int('A'), 0)
        self.assertEqual(var_to_int('B'), 1)
        self.assertEqual(var_to_int('Z'), 25)
        self.assertEqual(var_to_int('AA'), 26)
        self.assertEqual(var_to_int('AZ'), 51)
        self.assertEqual(var_to_int('BA'), 52)

    def testGetNextVariable(self):
        
        var_list = ["A", "C", "B"]
        self.assertEqual(get_next_variable_name(var_list), "D")
        
        var_list = ["A", "C", "Z"]
        self.assertEqual(get_next_variable_name(var_list), "AA")

        var_list = ["BC", "A", "B"]
        self.assertEqual(get_next_variable_name(var_list), "BD")
        
        var_list = ["A", "C", "BZ", "Z"]
        self.assertEqual(get_next_variable_name(var_list), "CA")
