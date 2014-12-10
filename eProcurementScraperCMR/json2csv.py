#!/usr/bin/python
'''
Created on Dec 5, 2014

@author: msuliga
'''

import json, sys, os


class JSON2CSV( object ):
    
    fileNameOut = 'json/alldata.csv'

    def convert_file( self, fileName ):

        keysSaved = False
        if os.path.exists( self.fileNameOut):
            keysSaved = True
            
        
        fileDescOut = open( self.fileNameOut, 'a' )
 

        with open( fileName ) as fileDescIn:
            for jsonLine in fileDescIn:

                jsonLine = jsonLine.rstrip()
                if jsonLine[0] == '[':
                    jsonLine = jsonLine[1:]
                jsonLine = jsonLine[:-1]

                try: 
                    jsonData = json.loads( jsonLine )
    
                    dataKeys = jsonData.keys()
    
                    if not keysSaved:
                        for key in dataKeys[:-1]:
                            fileDescOut.write( str( key ) + ',')
                        
                        fileDescOut.write( str( dataKeys[-1] ) + '\n')
                        
                        keysSaved = True
    
                    for key in dataKeys[:-1]:
                        fileDescOut.write( self.cleanData( str( jsonData[key] )) + ',')
                        
                    fileDescOut.write( self.cleanData(str( jsonData[dataKeys[-1]])) + '\n')
                    
                except ValueError:
                    pass

        fileDescOut.close()
        fileDescIn.close()

    def cleanData(self, dataEntry):
        
        dataEntry = dataEntry.replace('[', '').replace(']', '').replace(', ', ' -- ').replace(',', ' ')
        dataEntry = dataEntry.replace('quot;', '').replace('&quot', '').replace("u'", "").replace("'", "")
        
        return dataEntry.decode('ISO-8859-1')



if __name__ == '__main__':

    converter = JSON2CSV()
    converter.convert_file( sys.argv[1] )
