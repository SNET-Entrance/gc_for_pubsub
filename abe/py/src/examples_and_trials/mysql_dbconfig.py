'''
| From:    .
| Notes:    .

* type:          mysql 
* setting:             .
* assumption:    .

* example: 
** import: from mysql_dbconfig import *
** run: connect()

:authors: al
:date: 2015 
'''
from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser
#from fileinput import filename
import os
 
def read_db_config(fName='../../conf/config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param fName: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    if not(os.path.isfile(fName)):
        fName = os.path.join(os.path.dirname(__file__), fName)   
    parser = ConfigParser()    
    #os.path.dirname(__file__)
    #
    parser.read(fName)
 
    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, fName))
 
    return db

def connect(fName='../../conf/config.ini'):
    """ Connect to MySQL database """
 
    db_config = read_db_config(fName)
 
    try:
        print('Connecting to MySQL database...')
        conn = MySQLConnection(**db_config)
 
        if conn.is_connected():
            print('connection established.')
        else:
            print('connection failed.')
 
    except Error as error:
        print(error)
 
    finally:
        conn.close()
        print('Connection closed.')
 
 
if __name__ == '__main__':
    connect('../../conf/gm_config.ini')