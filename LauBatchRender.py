import os, nuke, shutil

COMP_PATH = "O:/14_NUKE_RENDER_TEMP"
BATCH_PATH = "O:/14_NUKE_RENDER_TEMP/BATCH"


class LauBatchRender(object):
    def __init__(self):

        self.nukeScriptPath = nuke.Root().name()

        try:
            self.filename = self.nukeScriptPath.split('/')[- 1].split('.')[- 2]
        except:
            nuke.message("Ce script n'est pas sauvegarde ! Cliquez sur OK pour quitter")
            return None

        self.lbrPanel = nuke.Panel("LauBatchRender |")

        self.lbrPanel.addSingleLineInput("Batch's name:", "queueRender")

        options = ('Queue', 'Parallel')
        options = ','.join(options)
        policyOpts = options.replace(',', ' ')
        self.lbrPanel.addEnumerationPulldown('Set localization policy', policyOpts)

        self.lbrPanel.addNotepad('Explications',
                                 'test')

        self.lbrPanel.addButton("Cancel")
        self.lbrPanel.addButton("Submit")

        self.action_result = self.lbrPanel.show()

        if self.action_result == 1:
            nuke.tprint("GO")

            return None
        else:
            nuke.tprint("ECHAPE")
            return None


lbr = LauBatchRender()
