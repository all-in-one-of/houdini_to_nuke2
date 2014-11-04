houdini_to_nuke.py
will transfer the houdini rendering nodes to nuke for image manipulation.

requirements:
houdini software and nuke sofware licences, (to be able to read the python bindings)


the ui will recolect the information of the houdini nodes.
will create a python file in a temp directory.
open nuke sofware in the same thread (lockin houdini) to avoid user interaction.
and nuke will read this created file loading the information provided by houdini.

the UI will let the user add new nodes to the interface.
move up, down, or delete nodes.
will let the user generate the result inside houdini,
 or transfer the information to nuke.

try to find lightplate, will attempt to collect information
of other department if exist and will use it as background.