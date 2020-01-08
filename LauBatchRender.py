# LauBatchRender - Simple way to create .bat for render !
# 2019 Laurette Alexandre - laurette.alexandre.free.fr
# April 2019
#
# Features:
# - Possibility to choose 3 type for render (Simple, Cue, Parallel)
# - Create a copy of the current script nuke
# - Before the lauchn of the app, check if folder BATCH_PATH and NUKE_SCRIPT_PATH exists. If not, Ask you if you want ti create them.

# To install this script, copy the LauBatchRender to your .nuke folder and put theses lines to your menu.py:
# import LauBatchRender
# # # toolbar.addCommand("LauBatchRender","LauBatchRender.start()", "^b", icon="WriteGeo.png")

################################################################################


# If python version < 3 :
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
# else imports Pyside for python 3
except:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *

import os, shutil, sys, uuid
import nuke

# GLOBAL VARIABLES (You may change theses values)

# Folder for .bat files
BATCH_PATH = 'D:/LAUBATCHRENDER'
# Folder for the copy of scripts nuke.
NUKE_SCRIPT_PATH = 'D:/LAUBATCHRENDER/SCRIPTS/'

################################################################################
###       DO NOT EDIT BELOW (unless you really know what you are doing)      ###
################################################################################

# UI
class LauBatchRenderUI(QWidget):
    def __init__(self):
        super(LauBatchRenderUI, self).__init__()

        self.setWindowTitle('LauBatchRender | laurette.alexandre.free.fr')
        self.resize(250, 230)

        batch_name_label = QLabel('Batch\'s name :')
        self.batch_name_input = QLineEdit()
        self.batch_name_input.setToolTip('The name the Batch File (only for Single Method)')

        frame_range_selection_label = QLabel('Frame Range :')
        self.frame_range_selection = QComboBox()

        start_frame_label = QLabel('Start Frame :')
        self.start_frame_input = QLineEdit()

        end_frame_label = QLabel('End Frame :')
        self.end_frame_input = QLineEdit()

        method_selection_label = QLabel('Method :')
        self.method_selection = QComboBox()
        self.method_selection.setToolTip('Single : one .bat for one render\nCue : one .bat for multiple render. Rendering will be done one after the other.\nParallel : one .bat for multiple render. All rendering will be launch in the same time.')
        self.method_selection.addItem('Single', 'Single')
        self.method_selection.addItem('Cue', 'Cue')
        self.method_selection.addItem('Parallel', 'Parallel')

        clear_cue_label = QLabel('Clear cue :')
        self.clear_cue_check = QCheckBox()
        self.clear_cue_check.setToolTip('Reset the content of cue.bat')

        clear_parallel_label = QLabel('Clear Parallel :')
        self.clear_parallel_check = QCheckBox()
        self.clear_parallel_check.setToolTip('Reset the content of Parallel.bat')

        self.validation_button = QPushButton('Ok')
        self.cancel_button = QPushButton('Cancel')

        left_layout = QVBoxLayout()
        left_layout.addWidget(batch_name_label)
        left_layout.addWidget(frame_range_selection_label)
        left_layout.addWidget(start_frame_label)
        left_layout.addWidget(end_frame_label)
        left_layout.addWidget(method_selection_label)

        clear_cue_layout = QHBoxLayout()
        clear_cue_layout.addWidget(clear_cue_label)
        clear_cue_layout.addWidget(self.clear_cue_check)

        clear_parallel_layout = QHBoxLayout()
        clear_parallel_layout.addWidget(clear_parallel_label)
        clear_parallel_layout.addWidget(self.clear_parallel_check)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.batch_name_input)
        right_layout.addWidget(self.frame_range_selection)
        right_layout.addWidget(self.start_frame_input)
        right_layout.addWidget(self.end_frame_input)
        right_layout.addWidget(self.method_selection)

        config_layout = QHBoxLayout()
        config_layout.addLayout(left_layout)
        config_layout.addLayout(right_layout)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.validation_button)
        action_layout.addWidget(self.cancel_button)

        master_layout = QVBoxLayout()
        master_layout.addLayout(config_layout)
        master_layout.addLayout(clear_cue_layout)
        master_layout.addLayout(clear_parallel_layout)
        master_layout.addLayout(action_layout)

        self.setLayout(master_layout)


class LauBatchRender(LauBatchRenderUI):
    def __init__(self):
        super(LauBatchRender, self).__init__()

        self.content = []

        # Init values
        self.nuke_script_path = nuke.Root().name()
        self.filename = self.nuke_script_path.split('/')[- 1].split('.')[- 2]
        self.nuke_from_frame = nuke.Root().firstFrame()
        self.nuke_to_frame = nuke.Root().lastFrame()
        self.nuke_executable_path = nuke.env['ExecutablePath']

        # Init framerange choice
        self.frame_range_selection.addItem('Project', '%s-%s' % (str(self.nuke_from_frame), str(self.nuke_to_frame)))
        self.frame_range_selection.addItem('Custom', '%s-%s' % (str(self.nuke_from_frame), str(self.nuke_to_frame)))

        # Get all viewer nodes
        for i in nuke.allNodes('Viewer'):
            self.frame_range_selection.addItem(i['name'].value(), i['frame_range'].value())

        # Put the default name : nuke script name
        self.batch_name_input.setText(self.filename)

        # Init default frame range
        self.start_frame_input.setText(str(self.nuke_from_frame))
        self.end_frame_input.setText(str(self.nuke_to_frame))

        # Signals
        self.frame_range_selection.currentIndexChanged.connect(self.updateFrameRange)
        self.validation_button.clicked.connect(self.runApp)
        self.cancel_button.clicked.connect(self.closeApp)

        # Check if batfile exist, if not, we create them
        self.checkBatchFile('Cue.bat')
        self.checkBatchFile('Parallel.bat')

    # Function to update frame range input thanks to the selection frame range
    def updateFrameRange(self):
        selection_frame_range = self.frame_range_selection.itemData(self.frame_range_selection.currentIndex())
        selection_frame_range = selection_frame_range.split('-')
        self.start_frame_input.setText(selection_frame_range[0])
        self.end_frame_input.setText(selection_frame_range[1])

    # Run the app
    def runApp(self):

        # Duplicate the script nuke for render
        self.copyNukeFile()

        # Check if we want to clear the cue.bat
        if self.clear_cue_check.isChecked():
            self.createBatchFile(os.path.join(BATCH_PATH, 'Cue.bat'))

        # Check if we want to clear the Parallel.bat
        elif self.clear_parallel_check.isChecked():
            self.createBatchFile(os.path.join(BATCH_PATH, 'Parallel.bat'))


        # If current selection is "Single", create the bat file with the custom name
        if self.method_selection.itemText(self.method_selection.currentIndex()) == 'Single':
            self.createBatchFile(os.path.join(BATCH_PATH, '%s.bat' % str(self.batch_name_input.text())))
            self.coreBatchFile()
            self.writeBatchFile(os.path.join(BATCH_PATH, '%s.bat' % str(self.batch_name_input.text())))

        elif self.method_selection.itemText(self.method_selection.currentIndex()) == 'Cue':
            self.getCoreBatchFile(os.path.join(BATCH_PATH, 'Cue.bat'))
            self.coreBatchFile()
            self.writeBatchFile(os.path.join(BATCH_PATH, 'Cue.bat'))

        elif self.method_selection.itemText(self.method_selection.currentIndex()) == 'Parallel':
            self.getCoreBatchFile(os.path.join(BATCH_PATH, 'Parallel.bat'))
            self.coreBatchFile()
            self.writeBatchFile(os.path.join(BATCH_PATH, 'Parallel.bat'))

        # Done ! We close the window and we say Bye Bye <3
        self.closeApp()

    # Thanks you, bye.
    def closeApp(self):
        self.close()

    # Check if the batch file (cue or Parallel) exist, if not, we create !
    def checkBatchFile(self, filename):
        if not os.path.isfile(os.path.join(BATCH_PATH, filename)):
            self.createBatchFile(os.path.join(BATCH_PATH, filename))

    # Create the base for batch file
    def createBatchFile(self, filename):
        try:
            with open(filename, 'w') as f:
                # Write header into the file
                f.write('@echo off\n')
                f.write('title LauBatchRender\n\n')

                if filename == os.path.join(BATCH_PATH, 'Parallel.bat'):
                    content = 'path="%s/"\n\n\n' % (os.path.dirname(self.nuke_executable_path))
                    f.write(content)
        except IOError:
            nuke.message('Unable to create %s' % filename)

    # Write the content of the file
    def writeBatchFile(self, filename):
        try:
            with open(filename, 'w') as f:
                for i in self.content:
                    # Write the content of the file
                    f.write(i)
        except IOError:
            nuke.message('Unable to write the file : %s !' % (filename))

    # Create the core content of the batch file depend of the selection
    def coreBatchFile(self):
        if self.method_selection.itemText(self.method_selection.currentIndex()) == 'Single':
            self.content.append('"%s" -x -F %s-%s "%s" \n\npause' % (self.nuke_executable_path, self.start_frame_input.text(), self.end_frame_input.text(), self.nuke_script_for_render))

        elif self.method_selection.itemText(self.method_selection.currentIndex()) == 'Cue':
            self.content.append('rem ============================\nrem SCRIPT FOR RENDER\nrem ============================\n\n')
            self.content.append('"%s" -x -F %s-%s "%s" \n\npause' % (self.nuke_executable_path, self.start_frame_input.text(), self.end_frame_input.text(), self.nuke_script_for_render))

        elif self.method_selection.itemText(self.method_selection.currentIndex()) == 'Parallel':
            self.content.append('rem ============================\nrem SCRIPT FOR RENDER\nrem ============================\n\n')
            self.content.append('start %s -x -F %s-%s %s \n\npause' % (os.path.basename(self.nuke_executable_path), self.start_frame_input.text(), self.end_frame_input.text(), self.nuke_script_for_render))

        else:
            print 'something is wrong !'

    # Get the original content of batch file (only for cue and Parallel
    def getCoreBatchFile(self, filename):
        with open(filename, 'r') as f:
            # get the content
            self.content = f.readlines()
            self.content.pop()

    # Create a copy of the current script
    def copyNukeFile(self):
        self.nuke_script_for_render = '%s%s_%s.nk' % (NUKE_SCRIPT_PATH, str(uuid.uuid1()), self.filename)
        try:
            shutil.copyfile(self.nuke_script_path, self.nuke_script_for_render)
        except IOError:
            nuke.message('Unable to create the file : %s ! The batch will not work ! Make shure you have theses following folders : %s and %s' % (self.nuke_script_for_render, BATCH_PATH, NUKE_SCRIPT_PATH))

def start():
    nuke_script_path = nuke.Root().name()

    try:
        filename = nuke_script_path.split('/')[- 1].split('.')[- 2]
    except:
        nuke.message('This script hasn\'t been saved yet. Press OK to cancel.')
        return None

    if not os.path.exists(BATCH_PATH):
        if nuke.ask('%s doesn\'t exist ! Do you want create this ?' % BATCH_PATH) is True:
            try:
                os.mkdir(BATCH_PATH)
            except:
                nuke.message('Impossible to create %s, create manually or check the right.')
                return None
        else:
            return None
    if not os.path.exists(NUKE_SCRIPT_PATH):
        if nuke.ask('%s doesn\'t exist ! Do you want create this ?' % NUKE_SCRIPT_PATH) is True:
            try:
                os.mkdir(NUKE_SCRIPT_PATH)
            except:
                nuke.message('Impossible to create %s, create manually or check the right.')
                return None
        else:
            return None

    # Start the app if all is good
    start.lbr = LauBatchRender()
    start.lbr.show()