#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
gc -- shortdesc

gc is a description

It defines classes_and_methods

@author:     al

@license:   MIT
            http://opensource.org/licenses/mit-license.php
            
@contact:    alex_foe@yahoo.de
@deffield    updated: Updated
'''

import sys, os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from model.config import Config
from model.db.sqlalchemy_declarative.gc import AbeGroupGm,AbeAttribute
from crypto.charm_abe import CharmAbe
from mqtt.pub_sub import Publisher, Subscriber

groupCfg = Config('conf/gc_config.ini')

__all__ = []
__version__ = 0.1
__date__ = '2015-06-11'
__updated__ = '2015-06-11'

DEBUG = 2
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s
  Created by al.
  Licensed under the MIT
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

  this is the GC, whenever a group is created, the GC adds himself to groupMember GM
Examples:
    ./gc.py groups
    ./gc.py grp_detail -g 1
    ./gc.py setup -n test -t "test/topic"
    ./gc.py add_gm -n "2.nd" -g 1
    ./gc.py sub -i 2
    ./gc.py pub -i 2 -m "here we go"
USAGE
''' % (program_shortdesc)
#, str(__date__)

    
    try:        
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        #FIXME: add abe-type: CPabe_BSW07, add curveType: SS512, MNT224
        parser.add_argument(dest="cmd", choices=['sub', 'pub', 'setup', 'rekey', 'groups', 'grp_detail', 'add_gm'], 
                            help="{ setup | pub | sub  | rekey | groups | add_gm | grp_detail}", nargs=1, metavar="cmd")
        parser.add_argument("-g", "--group_id", help="group_id: required for rekey, grp_detail and add_gm", nargs=1, type=int, metavar="group_id")
        parser.add_argument("-i", "--member_id", help="gm_id: required to run pub and sub", nargs=1, type=int, metavar="member_id")
        parser.add_argument("-m", "--message", help="message: required to run pub", nargs=1, metavar="message")
        parser.add_argument("-n", "--name", help="name: required for setup and add_gm", nargs=1, metavar="name")
        parser.add_argument("-t", "--topic", help="topic-name: required for setup ", nargs=1, metavar="topic")        
        #, required=True
        
        # Process arguments
        args = parser.parse_args()
        
        cmd = args.cmd[0]
        if DEBUG & 8:
            print(args)
            
        try:
            grpId = args.group_id[0]
        except:
            grpId = None
        try:
            inputName = args.name[0]
        except:
            inputName = None
        
#### the controler hide this somewhere else
        from model.db.sqlalchemy_declarative.gc import AbeGroupGc
        from model.db.data_access import DataAccess

        daoGC = DataAccess()
        daoGC.connect(groupCfg.getConfig('mysql'))
        daoGC.setSQLAlchemyModel(AbeGroupGc)
               
        if 'sub' == cmd:     
            try:
                gmId = args.member_id[0]
            except:
                gmId = None
            daoGM = DataAccess()
            daoGM.setSession(daoGC.getSession())
            daoGM.setSQLAlchemyModel(AbeGroupGm)
            rows = daoGM.get(gmId, 'id')            
            if len(rows) < 1:
                raise Exception('no data with id: ' + str(gmId) + ' found!')                                
            GM = rows[0]
            grpId = GM.gc_id
                        
            print("running mqtt client " + GM.name + ", now as subscriber, listening on: ", GM.mqtt_topic)            
            
            cfg = groupCfg.getConfig("mqtt_client")
            cfg['topic'] = GM.mqtt_topic
            cfg['dek'] = GM.dek
            cfg['client_id'] = gmId

            sub = Subscriber(cfg)
            sub.loop()
        elif 'pub' == cmd:
            try:
                gmId = args.member_id[0]
            except:
                gmId = None
                
            try:
                message = args.message[0]
            except:
                raise Exception('you must provide a message!')
                
            daoGM = DataAccess()
            daoGM.setSession(daoGC.getSession())
            daoGM.setSQLAlchemyModel(AbeGroupGm)
            rows = daoGM.get(gmId, 'id')            
            if len(rows) < 1:
                raise Exception('no data with id: ' + str(gmId) + ' found!')                                
            GM = rows[0]
            grpId = GM.gc_id
                        
            print("running mqtt client " + GM.name + ", now as publisher, listening on: ", GM.mqtt_topic)            
            
            cfg = groupCfg.getConfig("mqtt_client")
            cfg['topic'] = GM.mqtt_topic
            cfg['dek'] = GM.dek
            cfg['client_id'] = gmId

            pub = Publisher(cfg)
            pub.loop();
            pub.publish(message);
            pub.loop_end()

        elif 'groups' == cmd:
            print("printing all groups")
            for gc in daoGC.getAll():
                print(str(gc.id) + " | " + str(gc.name))
            print("done")
        elif 'grp_detail' == cmd:
            if grpId is None:
                raise Exception('no id provided for command: ' + cmd)
            elif not daoGC.isExists(grpId, 'id'):
                raise Exception('no data with id: ' + str(grpId) + ' found!')                                
            
            daoGM = DataAccess()
            daoGM.setSession(daoGC.getSession())
            daoGM.setSQLAlchemyModel(AbeGroupGm)
            
            daoAttr = DataAccess()
            daoAttr.setSession(daoGC.getSession())
            daoAttr.setSQLAlchemyModel(AbeAttribute)
            for gc in daoGC.get(grpId, 'id'): 
                print("the group: \n", 
                      daoGC.row2str(gc, ' | ', ['sk', 'dek', 'pk', 'mk']), 
                      "\nthe GMs:")#, daoGM.sqlAlchemyModel
                 
                for gm in daoGM.get(gc.id, 'gc_id'):
                    print (daoGM.row2str(gm, ' | ', ['sk', 'dek', 'sn_pk']))
                
                print("the attributes:")
                for attr in daoAttr.get(gc.id, 'gc_id'):
                    print (daoAttr.row2str(attr, ' | '))
                
                
        elif 'add_gm' == cmd:
            if inputName is None:
                raise Exception('no name provided for command: ' + cmd)
            if grpId is None:
                raise Exception('no id provided for command: ' + cmd)
            rows = daoGC.get(grpId, 'id')            
            if len(rows) < 1:
                raise Exception('no data with id: ' + str(grpId) + ' found!')                                
            GC = rows[0]
            if GC.abe_curve is None:
                raise Exception('GC is not setup: ' + str(grpId) + daoGC.row2str(GC))                                
            
            #updating the new GM, setting the SK to his attribute, which is his str(id)
            ABE = CharmAbe()
            ABE.setAbeCurveAndType(GC.abe_curve, GC.abe_type)
            newGM = AbeGroupGm(gc_id=GC.id,
               name="the GC",                 
               dek=GC.dek,
               mqtt_topic=GC.mqtt_topic,
               sn_pk=GC.pk,
               sn_abe_type=GC.abe_type,
               sn_abe_curve=GC.abe_curve) 
            newAttr = daoGC.addGMwithNoSK(newGM)
            newGM.sk = ABE.keygen(GC.pk, GC.mk, [str(newAttr.value)]) 
            daoGC.updateGM(newGM)
            print("new GM added with id: " + str(newGM.id) + ", to group_id: " + str(grpId))

        elif 'setup' == cmd:            
            if inputName is None:
                raise Exception('no name provided for command: ' + cmd)
            try:
                topic = args.topic[0]
            except:
                raise Exception('no topic provided for command: ' + cmd)
            
            ABE = CharmAbe()
            abeType = 'CPabe_BSW07' #FIXME: as input plz
            abeCurve= 'SS512'       #FIXME: as input plz
            ABE.setAbeCurveAndType(abeCurve, abeType)
            (serPK, serMK) = ABE.setup()
            DEK = ABE.getDEK()
            newGRP = AbeGroupGc(name=inputName,
                                mqtt_topic=topic, 
                                pk=serPK, 
                                mk=serMK, 
                                dek=DEK, 
                                abe_type=abeType, 
                                abe_curve=abeCurve)
            daoGC.addGroup(newGRP)
            
            newGM = AbeGroupGm(gc_id=newGRP.id,
                           name="the GC",                             
                           dek=DEK,
                           mqtt_topic=topic,
                           sn_pk=serPK,
                           sn_abe_type=abeType,
                           sn_abe_curve=abeCurve)        
            
            #updating the new GM, setting the SK to his attribute, which is his str(id)            
            newAttr = daoGC.addGMwithNoSK(newGM)
            if  newGM.id < 1: 
                print("new GM was not stored correctly, id is empty", newGM)
                raise Exception("new GM was not stored correctly, id is empty")
                                    
            newGM.sk = ABE.keygen(serPK, serMK, [str(newAttr.value)]) 
            daoGC.updateGM(newGM)

            print('new group added with id: ' + str(newGRP.id), "\nand GM added with id: " + str(newGM.id))
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
'''    
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        
        indent = len(program_inputName) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
    except:
        print("Unexpected error:", sys.exc_info()[0])
            
        indent = len(program_name) * " "
        sys.stderr.write(indent + "  for help use --help")
        return 2    
'''
if __name__ == "__main__":
#    if DEBUG:
#        sys.argv.append("-h")
#        sys.argv.append("-v")
#        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'gc_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
    #main()