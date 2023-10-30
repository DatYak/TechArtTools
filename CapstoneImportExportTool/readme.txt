Level Exporter and Importer
Made by Isaac Lovy for Moles In a Bowl

TO USE:
Place 'LevelExporter.py' in the maya project scripts directory. MAYA DIRECTORY
Add the following code as a shelf button:

import maya.cmds as cmds
import sys
workspace_path = cmds.workspace( q=True, rd=True )
workspace_path += 'scripts'
sys.path.append(workspace_path)
import levelExporter
levelExporter.launch_import_export()
