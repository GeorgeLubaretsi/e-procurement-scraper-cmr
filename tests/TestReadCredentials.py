'''
Created on Nov 5, 2014

@author: msuliga
'''
import unittest
from CMRCredentials import CMRCredentials


class Test(unittest.TestCase):
    ''' 
    Testing if the credentials are present and are correctly formatted.
    '''

    def test_read_credentials(self):
        cmrCreds = CMRCredentials()
        
        creds = cmrCreds.load_credentials()
        
        self.assertIsNotNone( creds, "Can't read credentials file")
        self.assertIsInstance( creds, dict, "Format error: credentials need to be returned as a dictionary")
        
        self.assertIsNotNone( creds[ 'username'], 'No "username" in credentials')
        self.assertIsNotNone( creds[ 'password'], 'No "password" in credentials')
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_read_credentials']
    unittest.main()