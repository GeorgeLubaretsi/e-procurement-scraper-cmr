'''
Created on Nov 5, 2014

@author: msuliga
'''

import ConfigParser
import os

class CMRCredentials(object):
    '''
    classdocs
    '''
    credFileInfo = '''
     The credentials have to be stored in file $HOME/.cmrcreds.
     The format of the file:
     
     [cmr]
     username=
     password=
     
     ''' 

    def __init__(self):
        '''
        Constructor
        '''
        self.creds_filename = '%s/.cmrcreds' % os.getenv('HOME')
        self.login_name = None
        self.login_passwd = None
        
    # the credentials will be loaded from home folder from .cmrcreds file ($HOME/.cmrcreds)
    def load_credentials(self):
        config = ConfigParser.RawConfigParser( allow_no_value = False)
        
        if not os.path.isfile(self.creds_filename):
            print self.credFileInfo
            raise Exception
            
        config.read(self.creds_filename)
        self.login_name = config.get('cmr', 'username')
        self.login_passwd = config.get( 'cmr', 'password')
        return {'username' : self.login_name, 'password' : self.login_passwd}
        
if __name__ == '__main__':
    creds = CMRCredentials()
    creds.load_credentials()
    print creds.login_name + " : " + creds.login_passwd