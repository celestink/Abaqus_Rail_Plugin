from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='TrackPreprocess', 
    object=Activator(os.path.join(thisDir, 'myrailroadDB.py')),
    kernelInitString='import trackStifVar',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=ALL,
    version='1.0.1',
    author='Celestin Nkundineza,PhD',
    description= 'Affiliation: The University of Nebraska- Lincoln. \n\n'\
	'This GUI helps you quickly do the preprocessing of railroad track '\
	'parameterized by  spatial variations of track stiffness as well as loads.\n\n'\
	'Also, you can choose to use a simple rail geometry or an exact rail geometry.'\
	'Other flexibilities include your choice to use static loads or dynamic loads.\n\n'\
	'This plug-in will generate multiple inp files with respect to statistical data inputs of crosstie moduli.\n'\
	'It will also generate files that contain crosstie moduli per each track.'\
    'Note: version 1.0.1 adds periodic boundary conditions on the crosstie sides at the ends of the track \n\n'\
	"This plug-in's files may be copied from " +thisDir+ "\n"\
	'For any other question please contact the author at cn@huskers.unl.edu',
    helpUrl='N/A'
)
