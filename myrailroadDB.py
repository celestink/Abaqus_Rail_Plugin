# Do not edit this file or it may not load correctly
# if you try to open it with the RSG Dialog Builder.

# Note: thisDir is defined by the Activator class when
#       this file gets exec'd

from rsg.rsgGui import *
from abaqusConstants import INTEGER, FLOAT
dialogBox = RsgDialog(title='Abaqus Rail', kernelModule='trackStifVar', kernelFunction='TrackModel', includeApplyBtn=True, includeSeparator=True, okBtnText='OK', applyBtnText='Apply', execDir=thisDir)
RsgTabBook(name='TabBook_1', p='DialogBox', layout='0')
RsgTabItem(name='TabItem_4', p='TabBook_1', text='Load data')
RsgComboBox(name='ComboBox_5', p='TabItem_4', text='Loading behaviour', keyword='loadtype', default='Static', comboType='STANDARD', repository='', rootText='', rootKeyword='None', layout='')
RsgListItem(p='ComboBox_5', text='Static')
RsgListItem(p='ComboBox_5', text='Dynamic')
RsgCheckButton(p='TabItem_4', text='Maximum computed steps', keyword='maxsteps', default=True)
RsgTextField(p='TabItem_4', fieldType='Integer', ncols=12, labelText='Number of load steps', keyword='numsteps', default='1')
RsgCheckButton(p='TabItem_4', text='Apply Periodic BC', keyword='APBC', default=True)
RsgTabItem(name='TabItem_1', p='TabBook_1', text='Crossties data')
RsgTextField(p='TabItem_1', fieldType='Float', ncols=12, labelText='Lenth of the crosstie', keyword='Tielength', default='457.2')
RsgTextField(p='TabItem_1', fieldType='Float', ncols=12, labelText='depth of the crosstie', keyword='Tiedepth', default='177.2')
RsgTextField(p='TabItem_1', fieldType='Integer', ncols=12, labelText='Number of crosstie', keyword='nt', default='10')
RsgTabItem(name='TabItem_2', p='TabBook_1', text='Rail Track data')
RsgGroupBox(name='GroupBox_1', p='TabItem_2', text='track diagrams', layout='0')
#RsgIcon(p='GroupBox_1', fileName='rectarail.png')
RsgIcon(p='GroupBox_1', fileName='railmodels.png')
RsgComboBox(name='ComboBox_6', p='TabItem_2', text='Rail  Model geometry', keyword='railgeom', default='Rectangular', comboType='STANDARD', repository='', rootText='', rootKeyword='None', layout='')
RsgListItem(p='ComboBox_6', text='Rectangular')
RsgListItem(p='ComboBox_6', text='Exact')
RsgTextField(p='TabItem_2', fieldType='Float', ncols=12, labelText='Rail distance between tie center to next tie centers', keyword='lin', default='266.7')
RsgTextField(p='TabItem_2', fieldType='Float', ncols=12, labelText='Incremental distance beetween load positions', keyword='dz', default='266.7')
RsgTextField(p='TabItem_2', fieldType='Float', ncols=12, labelText='mesh element global size', keyword='meshsize', default='6.0')
RsgTabItem(name='TabItem_3', p='TabBook_1', text='Statistical data')
RsgTextField(p='TabItem_3', fieldType='Float', ncols=12, labelText='Minimum value of the modulus', keyword='minmod', default='20.0')
RsgGroupBox(name='GroupBox_5', p='TabItem_3', text='Moduli Standrd Deviation variations', layout='LAYOUT_FILL_X')
RsgTextField(p='GroupBox_5', fieldType='Float', ncols=12, labelText='Increment', keyword='SDincr', default='20.0')
RsgTextField(p='GroupBox_5', fieldType='Integer', ncols=12, labelText='Number of increments', keyword='nSDi', default='1')
RsgTextField(p='GroupBox_5', fieldType='Integer', ncols=12, labelText='Repetitions of a realization', keyword='nrepeat', default='1')
RsgGroupBox(name='GroupBox_4', p='TabItem_3', text='Moduli mean variations', layout='0')
RsgTextField(p='GroupBox_4', fieldType='Float', ncols=12, labelText='Mean', keyword='modmean', default='300.0')
RsgVerticalAligner(name='VAligner_1', p='GroupBox_4', pl=0, pr=0, pt=0, pb=0)
dialogBox.show()