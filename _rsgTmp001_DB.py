from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class _rsgTmp001_DB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Abaqus Rail',
            self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            

        applyBtn = self.getActionButton(self.ID_CLICKED_APPLY)
        applyBtn.setText('Apply')
            
        TabBook_1 = FXTabBook(p=self, tgt=None, sel=0,
            opts=TABBOOK_NORMAL,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING)
        tabItem = FXTabItem(p=TabBook_1, text='Load data', ic=None, opts=TAB_TOP_NORMAL,
            x=0, y=0, w=0, h=0, pl=6, pr=6, pt=DEFAULT_PAD, pb=DEFAULT_PAD)
        TabItem_4 = FXVerticalFrame(p=TabBook_1,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        ComboBox_5 = AFXComboBox(p=TabItem_4, ncols=0, nvis=1, text='Loading behaviour', tgt=form.loadtypeKw, sel=0)
        ComboBox_5.setMaxVisible(10)
        ComboBox_5.appendItem(text='Static')
        ComboBox_5.appendItem(text='Dynamic')
        FXCheckButton(p=TabItem_4, text='Maximum computed steps', tgt=form.maxstepsKw, sel=0)
        AFXTextField(p=TabItem_4, ncols=12, labelText='Number of load steps', tgt=form.numstepsKw, sel=0)
        FXCheckButton(p=TabItem_4, text='Apply Periodic BC', tgt=form.APBCKw, sel=0)
        tabItem = FXTabItem(p=TabBook_1, text='Crossties data', ic=None, opts=TAB_TOP_NORMAL,
            x=0, y=0, w=0, h=0, pl=6, pr=6, pt=DEFAULT_PAD, pb=DEFAULT_PAD)
        TabItem_1 = FXVerticalFrame(p=TabBook_1,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        AFXTextField(p=TabItem_1, ncols=12, labelText='Lenth of the crosstie', tgt=form.TielengthKw, sel=0)
        AFXTextField(p=TabItem_1, ncols=12, labelText='depth of the crosstie', tgt=form.TiedepthKw, sel=0)
        AFXTextField(p=TabItem_1, ncols=12, labelText='Number of crosstie', tgt=form.ntKw, sel=0)
        tabItem = FXTabItem(p=TabBook_1, text='Rail Track data', ic=None, opts=TAB_TOP_NORMAL,
            x=0, y=0, w=0, h=0, pl=6, pr=6, pt=DEFAULT_PAD, pb=DEFAULT_PAD)
        TabItem_2 = FXVerticalFrame(p=TabBook_1,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        GroupBox_1 = FXGroupBox(p=TabItem_2, text='track diagrams', opts=FRAME_GROOVE)
        fileName = os.path.join(thisDir, 'railmodels.png')
        icon = afxCreatePNGIcon(fileName)
        FXLabel(p=GroupBox_1, text='', ic=icon)
        ComboBox_6 = AFXComboBox(p=TabItem_2, ncols=0, nvis=1, text='Rail  Model geometry', tgt=form.railgeomKw, sel=0)
        ComboBox_6.setMaxVisible(10)
        ComboBox_6.appendItem(text='Rectangular')
        ComboBox_6.appendItem(text='Exact')
        AFXTextField(p=TabItem_2, ncols=12, labelText='Rail distance between tie center to next tie centers', tgt=form.linKw, sel=0)
        AFXTextField(p=TabItem_2, ncols=12, labelText='Incremental distance beetween load positions', tgt=form.dzKw, sel=0)
        AFXTextField(p=TabItem_2, ncols=12, labelText='mesh element global size', tgt=form.meshsizeKw, sel=0)
        tabItem = FXTabItem(p=TabBook_1, text='Statistical data', ic=None, opts=TAB_TOP_NORMAL,
            x=0, y=0, w=0, h=0, pl=6, pr=6, pt=DEFAULT_PAD, pb=DEFAULT_PAD)
        TabItem_3 = FXVerticalFrame(p=TabBook_1,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        AFXTextField(p=TabItem_3, ncols=12, labelText='Minimum value of the modulus', tgt=form.minmodKw, sel=0)
        GroupBox_5 = FXGroupBox(p=TabItem_3, text='Moduli Standrd Deviation variations', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        AFXTextField(p=GroupBox_5, ncols=12, labelText='Increment', tgt=form.SDincrKw, sel=0)
        AFXTextField(p=GroupBox_5, ncols=12, labelText='Number of increments', tgt=form.nSDiKw, sel=0)
        AFXTextField(p=GroupBox_5, ncols=12, labelText='Repetitions of a realization', tgt=form.nrepeatKw, sel=0)
        GroupBox_4 = FXGroupBox(p=TabItem_3, text='Moduli mean variations', opts=FRAME_GROOVE)
        AFXTextField(p=GroupBox_4, ncols=12, labelText='Mean', tgt=form.modmeanKw, sel=0)
        VAligner_1 = AFXVerticalAligner(p=GroupBox_4, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0)
