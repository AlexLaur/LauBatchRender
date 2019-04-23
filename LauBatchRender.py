try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *

import os, shutil, sys, uuid
import nuke

# GLOBAL VARIABLES

NUKE_SCRIPT_PATH = "D:/LAUBATCHRENDER/SCRIPTS/"

BATCH_PATH = "D:/LAUBATCHRENDER/"

################################################################################
###       DO NOT EDIT BELOW (unless you really know what you are doing)      ###
################################################################################

# UI
class LauBatchRenderUI(QWidget):
    def __init__(self):
        super(LauBatchRenderUI, self).__init__()

        self.setWindowTitle("LauBatchRender | laurette.alexandre.free.fr")
        self.resize(250, 300)

        batch_name_label = QLabel("Batch's name :")
        self.batch_name_input = QLineEdit()
        self.batch_name_input.setToolTip("The name the Batch File (only for Single Method)")

        frame_range_selection_label = QLabel("Frame Range :")
        self.frame_range_selection = QComboBox()

        start_frame_label = QLabel("Start Frame :")
        self.start_frame_input = QLineEdit()

        end_frame_label = QLabel("End Frame :")
        self.end_frame_input = QLineEdit()

        method_selection_label = QLabel("Method :")
        self.method_selection = QComboBox()
        self.method_selection.addItem("Single", "Single")
        self.method_selection.addItem("Queue", "Queue")
        self.method_selection.addItem("Parallel", "Parallel")

        clear_queue_label = QLabel("Clear Queue :")
        self.clear_queue_check = QCheckBox()

        clear_parallel_label = QLabel("Clear Parallel :")
        self.clear_parallel_check = QCheckBox()

        self.validation_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")

        left_layout = QVBoxLayout()
        left_layout.addWidget(batch_name_label)
        left_layout.addWidget(frame_range_selection_label)
        left_layout.addWidget(start_frame_label)
        left_layout.addWidget(end_frame_label)
        left_layout.addWidget(method_selection_label)
        # left_layout.addWidget(clear_queue_label)
        # left_layout.addWidget(clear_parallel_label)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.batch_name_input)
        right_layout.addWidget(self.frame_range_selection)
        right_layout.addWidget(self.start_frame_input)
        right_layout.addWidget(self.end_frame_input)
        right_layout.addWidget(self.method_selection)
        # right_layout.addWidget(self.clear_queue_check)
        # right_layout.addWidget(self.clear_parallel_check)

        config_layout = QHBoxLayout()
        config_layout.addLayout(left_layout)
        config_layout.addLayout(right_layout)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.validation_button)
        action_layout.addWidget(self.cancel_button)

        master_layout = QVBoxLayout()
        master_layout.addLayout(config_layout)
        master_layout.addLayout(action_layout)

        self.setLayout(master_layout)


class LauBatchRender(LauBatchRenderUI):
    def __init__(self):
        super(LauBatchRender, self).__init__()

        # Init values
        self.nuke_script_path = nuke.Root().name()
        self.filename = self.nuke_script_path.split('/')[- 1].split('.')[- 2]
        self.nuke_from_frame = nuke.Root().firstFrame()
        self.nuke_to_frame = nuke.Root().lastFrame()
        self.nuke_executable_path = nuke.env["ExecutablePath"]

        # Init framerange choice
        self.frame_range_selection.addItem("Project", str(self.nuke_from_frame) + "-" + str(self.nuke_to_frame))
        self.frame_range_selection.addItem("Custom", str(self.nuke_from_frame) + "-" + str(self.nuke_to_frame))

        # Get all viewer nodes
        for i in nuke.allNodes("Viewer"):
            self.frame_range_selection.addItem(i["name"].value(), i['frame_range'].value())

        # Put the default name : nuke script name
        self.batch_name_input.setText(self.filename)

        # Init default frame range
        self.start_frame_input.setText(str(self.nuke_from_frame))
        self.end_frame_input.setText(str(self.nuke_to_frame))

        # Signals
        self.frame_range_selection.currentIndexChanged.connect(self.updateFrameRange)
        self.validation_button.clicked.connect(self.runApp)
        self.cancel_button.clicked.connect(self.closeApp)

    # Function to update frame range input thanks to the selection frame range
    def updateFrameRange(self):
        selection_frame_range = self.frame_range_selection.itemData(self.frame_range_selection.currentIndex())
        selection_frame_range = selection_frame_range.split("-")
        self.start_frame_input.setText(selection_frame_range[0])
        self.end_frame_input.setText(selection_frame_range[1])

    # Run the app
    def runApp(self):

        # Check if batfile exist, if not, we create them
        self.checkBatchFile("Queue.bat")
        self.checkBatchFile("Parallel.bat")

        # If current selection is "Single", create the bat file with the custom name
        if self.method_selection.itemText(self.method_selection.currentIndex()) == "Single":
            self.createBatchFile(BATCH_PATH + str(self.batch_name_input.text()) + ".bat")

        # Duplicate the script nuke for render
        self.copyNukeFile()

    # Thanks you, bye.
    def closeApp(self):
        self.close()

    # Check if the batch file (Queue or Parallel) exist, if not, we create !
    def checkBatchFile(self, filename):
        if not os.path.isfile(BATCH_PATH + filename):
            self.createBatchFile(BATCH_PATH + filename)

    # Create the base for batch file
    def createBatchFile(self, filename):
        with open(filename, 'wb') as f:
            # Write header into the file
            f.write("@echo off\n")
            f.write("title LauBatchRender\n\n")

    # Write the content of the file
    def writeBatchFile(self, filename):
        print "test"

    # Create the core content of the batch file depend of the selection
    def coreBatchFile(self):
        if self.method_selection.itemText(self.method_selection.currentIndex()) == "Single":
            print "single"
        elif self.method_selection.itemText(self.method_selection.currentIndex()) == "Queue":
            print "queue"
        elif self.method_selection.itemText(self.method_selection.currentIndex()) == "Parallel":
            print "parallel"
        else:
            print "something is wrong !"


        print "core"
        self.content = "tt"

    # Create a copy of the current script
    def copyNukeFile(self):
        self.nuke_script_for_render = NUKE_SCRIPT_PATH + str(uuid.uuid1()) + "_" + self.filename
        shutil.copyfile(self.nuke_script_path, self.nuke_script_for_render)


def start():
    nuke_script_path = nuke.Root().name()
    try:
        filename = nuke_script_path.split('/')[- 1].split('.')[- 2]
    except:
        nuke.message("This script hasn't been saved yet. Press OK to cancel.")
        return None

    start.lbr = LauBatchRender()
    start.lbr.show()


start()

# app = QApplication(sys.argv)
# lbr = LauBatchRender()
# lbr.show()
# app.exec_()
