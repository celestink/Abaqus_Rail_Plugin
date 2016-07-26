from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class _rsgTmp001_Form(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='TrackModel',
            objectName='trackStifVar', registerQuery=False)
        pickedDefault = ''
        self.loadtypeKw = AFXStringKeyword(self.cmd, 'loadtype', True, 'Static')
        self.maxstepsKw = AFXBoolKeyword(self.cmd, 'maxsteps', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.numstepsKw = AFXIntKeyword(self.cmd, 'numsteps', True, 1)
        self.APBCKw = AFXBoolKeyword(self.cmd, 'APBC', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.TielengthKw = AFXFloatKeyword(self.cmd, 'Tielength', True, 457.2)
        self.TiedepthKw = AFXFloatKeyword(self.cmd, 'Tiedepth', True, 177.2)
        self.ntKw = AFXIntKeyword(self.cmd, 'nt', True, 10)
        self.railgeomKw = AFXStringKeyword(self.cmd, 'railgeom', True, 'Rectangular')
        self.linKw = AFXFloatKeyword(self.cmd, 'lin', True, 266.7)
        self.dzKw = AFXFloatKeyword(self.cmd, 'dz', True, 266.7)
        self.meshsizeKw = AFXFloatKeyword(self.cmd, 'meshsize', True, 6.0)
        self.minmodKw = AFXFloatKeyword(self.cmd, 'minmod', True, 20.0)
        self.SDincrKw = AFXFloatKeyword(self.cmd, 'SDincr', True, 20.0)
        self.nSDiKw = AFXIntKeyword(self.cmd, 'nSDi', True, 1)
        self.nrepeatKw = AFXIntKeyword(self.cmd, 'nrepeat', True, 1)
        self.modmeanKw = AFXFloatKeyword(self.cmd, 'modmean', True, 300.0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import _rsgTmp001_DB
        return _rsgTmp001_DB._rsgTmp001_DB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[ kw1.getValue() ]
                kw2.setValue(value)
            except:
                pass
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def deactivate(self):
    
        try:
            osutils.remove(os.path.join('c:\\Users\\celestink\\abaqus_plugins\\myrailroad', '_rsgTmp001_DB.py'), force=True )
            osutils.remove(os.path.join('c:\\Users\\celestink\\abaqus_plugins\\myrailroad', '_rsgTmp001_DB.pyc'), force=True )
        except:
            pass
        try:
            osutils.remove(os.path.join('c:\\Users\\celestink\\abaqus_plugins\\myrailroad', '_rsgTmp001_Form.py'), force=True )
            osutils.remove(os.path.join('c:\\Users\\celestink\\abaqus_plugins\\myrailroad', '_rsgTmp001_Form.pyc'), force=True )
        except:
            pass
        AFXForm.deactivate(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getCommandString(self):

        cmds = 'import trackStifVar\n'
        cmds += AFXForm.getCommandString(self)
        return cmds

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False
