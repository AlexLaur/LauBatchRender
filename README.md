# LauBatchRender

LauBatchRender is a simple way to create .bat scripts to render your comp. Choose if you want render in Single, Cue or Parallel.

- Single : one .bat for one render
- Cue : one .bat for multiple render. Rendering will be done one after the other.
- Parallel : one .bat for multiple render. All rendering will be launch in the same time. 

To install
----------

- Download the LauBatchRender.py and copy this file to your .nuke folder.
- Then, edit you menu.py and add this :

      import LauBatchRender
      toolbar.addCommand('LauBatchRender','LauBatchRender.start()', '^b', icon='WriteGeo.png')

The icon is present inside nuke but  if you want, you can use a custom icon.

Compatibility
-------------

Tested on Nuke 11.2v3 and Nuke 10.0v2

Future update
-------------

- Improve the translation (Sorry I am French)

- Possibility to create .sh for Linux and OS X. 

If you have any ideas to improve this script. Let's get in touch ! 
