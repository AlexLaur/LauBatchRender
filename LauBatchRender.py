import os, nuke, shutil

COMP_PATH = "O:/14_NUKE_RENDER_TEMP"

BATCH_PATH = "O:/14_NUKE_RENDER_TEMP/BATCH"

class LauBatchRender(object):
    def __init__(self):
        
        self.nukeScriptPath = nuke.Root().name()
        self.nukeFromFrame = nuke.Root().firstFrame()
        self.nukeToFrame = nuke.Root().lastFrame()

        try:
            self.filename = self.nukeScriptPath.split('/')[- 1].split('.')[- 2]
        except:
            nuke.message("This script hasn't been saved yet. Press OK to cancel.")
            return None

        self.lbrPanel = nuke.Panel("LauBatchRender | laurette.alexandre.free.fr")

        self.lbrPanel.addSingleLineInput("Batch's name:", self.filename)

        self.lbrPanel.addSingleLineInput("Start Frame :", self.nukeFromFrame)
        self.lbrPanel.addSingleLineInput("End Frame :", self.nukeToFrame)

        options = ('Single', 'Queue', 'Parallel')
        options = ','.join(options)
        policyOpts = options.replace(',',' ')
        self.lbrPanel.addEnumerationPulldown('Select the method', policyOpts)

        self.lbrPanel.addBooleanCheckBox('Clear Queue', False)
        self.lbrPanel.addBooleanCheckBox('Clear Parallel', False)

        #self.lbrPanel.addNotepad('Infos','')

        self.lbrPanel.addButton("Cancel")
        self.lbrPanel.addButton("Submit")

        self.action_result = self.lbrPanel.show()

        if self.action_result == 1:
            nuke.tprint("GO")
            nuke.tprint(self.lbrPanel.value("Select the method"))
            self.checkInputUser()

            return None
        else:
            nuke.tprint("ECHAPE")
            return None


    def checkInputUser(self):
        nuke.tprint("check input users")


lbr = LauBatchRender()
