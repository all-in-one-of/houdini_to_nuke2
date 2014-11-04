###python
# author demian kurejwowski
#version 1.0.1
"""
Added
if nothing is selected will add all rfxmantra nodes to the list.
"""
#to do:
'''
# check and fix if the render is single eye,  example just right eye and get the _l  see what happen

DONE: button added to the interface to connect a function that will try to find the plates of lighting and will merge them before the final output.
fixed: now you can lunch the program with one node and wont error connecting the last write node to the non existing temp_composite (use a try/except)
'''

import sys
import os
#importing the classes from The Foundry Nuke software
import nuke_tools
#importing the classes from Side Effects Houdini software
import hou

from PyQt4 import QtCore
from PyQt4 import QtGui

#appending the path of the PyQTHoudini(this will run PyQt in a different thread)
hou_version = hou.applicationVersionString()
sys.path.append("/opt/hfs"+hou_version+"/houdini/help/hom/cookbook/pyqt/part1/")
import pyqt_houdini

# ICONS
# path for the icons used in the UI
Delete_Icon = '/mounts/elmo/code/global/icons/ui/ui_lib_old/Delete_24x24.png'
Down_Icon ='/mounts/elmo/code/global/icons/ui/ui_lib_old/Down_24x24.png'
Up_Icon ='/mounts/elmo/code/global/icons/ui/ui_lib_old/Up_24x24.png'

houdini_Icon = "/mounts/elmo/code/global/icons/houdini_logo_large.png"
nuke_Icon = "/mounts/elmo/code/global/icons/nuke_logo_large.png"

class myList(QtGui.QTableWidget):
    def __init__(self,parent):
        super(myList,self).__init__(parent)

        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setAlternatingRowColors(True)
        self.resizeColumnsToContents()
        self.setWordWrap(1)

    def getTextOfCurrentCell(self):
        print "ENTER"
        print self.currentItem().text()

#    def printer(self):
#        print self.currentRow()
#        print self.supportedDropActions()

    def dragEnterEvent(self,event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
          super(myList, self).dragEnterEvent(event)

    def dropEvent(self,event):
        position = event.pos()
        overText =  self.itemAt(position).text()
        overItem =  self.itemAt(position)

        overItem.setText(self.currentItem().text())

        SavedText =  self.currentItem().text()
        SavedText = overText
        self.currentItem().setText(SavedText)

class PreComp(QtGui.QWidget):
    def show_sure_to_reset(self):
        self.to_reset = sure_to_reset(self)
        self.to_reset.show()
#        self.to_reset.exec_() # Modal,  this make a relation between windows.

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
        self.setGeometry(300,300,700,800)
        self.setWindowTitle("Pre Comp Houdini")

        main_layout = QtGui.QVBoxLayout(self)

        self.table = myList(self)

        self.table.setColumnCount(4)
        self.table.setColumnWidth(0,300)
        self.table.setHorizontalHeaderLabels(["Render Nodes","","",""])
        self.table.horizontalHeader().setStretchLastSection(True)

        self.reset_btn = QtGui.QPushButton("Reset to Default List")
        main_layout.addWidget(self.reset_btn)

        main_layout.addWidget(self.table)

        self.add_more_nodes_btn = QtGui.QPushButton("Add More Nodes")
        self.add_more_nodes_btn.setToolTip("this will let you select more mantra nodes, and add them to the list")
		self.add_more_nodes_btn.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)

        self.lower_apps_layout = QtGui.QHBoxLayout()

        self.construct_hou_btn = QtGui.QPushButton("PreComp Houdini")
        self.construct_hou_btn.setToolTip("this will create a precomp after the last selected node in the order of the table top-down")
		self.construct_hou_btn.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)

        h_Icon = QtGui.QIcon(houdini_Icon)
        self.construct_hou_btn.setIcon(h_Icon)
        self.construct_hou_btn.setMinimumHeight(50)

        self.platesCheckBox = QtGui.QCheckBox("Try to find Light Plates")
        self.platesCheckBox.setToolTip("will try to find the latest plates from lighting")
        self.platesCheckBox.setCheckState(2)

        self.construct_nuke_btn = QtGui.QPushButton("PreComp Nuke")
        self.construct_nuke_btn.setToolTip("this will create a precomp after the last selected node in the order of the table top-down")
		self.construct_nuke_btn.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)
        n_Icon = QtGui.QIcon(nuke_Icon)
        self.construct_nuke_btn.setIcon(n_Icon)
        self.construct_nuke_btn.setMinimumHeight(50)

        self.lower_apps_layout.addWidget(self.construct_hou_btn)
        self.lower_apps_layout.addWidget(self.platesCheckBox)
        self.lower_apps_layout.addWidget(self.construct_nuke_btn)

		# setting up the layouts-----------------------------------------------------
        main_layout.addWidget(self.add_more_nodes_btn)
        main_layout.addLayout(self.lower_apps_layout)
        self.setLayout(main_layout)

		# Making the connections-----------------------------------------------------
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor ))
        self.table.cellClicked.connect(self.on_click)
        self.table.cellClicked.connect(self.icon_buttons_def)
		# Here we pop a new windows making sure if the user want to reset to the initial list on the UI----------------------
        self.reset_btn.clicked.connect(self.reset)
		self.add_more_nodes_btn.released.connect(self.add_more_nodes)

        self.construct_nuke_btn.released.connect(self.preComp_nuke)
        self.construct_hou_btn.released.connect(self.runn)

		#filtering just RFXMANTRA nodes,  nothing else will get into the UI
        self.selected_nodes = []
        if len(hou.selectedNodes() ) == 0:
            if_selected_list = hou.node("/").allSubChildren()
        else:
            if_selected_list = hou.selectedNodes()
        for i in if_selected_list:
            if i.type().nameComponents()[2]== "rfxMantra" or i.type().nameComponents()[2] == "ifd":
                self.selected_nodes.append(i)

        self.populate_table(self.selected_nodes)

# PRECOMP NUKE  here we start the scrip that Nuke will run to create the file-----------------------------
    def preComp_nuke(self):
        print "preComp_nuke"
        temp_path = "/tmp/pre_comp.py"
        if temp_path:
            open(temp_path,"w").close()

        file = open(temp_path,"w")
        dict_list = []

        render_type = "None"
        stereo_render = "None"
        dtex = "None"

        for row in xrange(0,self.table.rowCount()):
            list_attributes = []
            item = str(self.table.item(row,0).text())
            mnode = hou.node( str(item) )
            mnode_image_path = mnode.parm("vm_picture").eval()
            h = mnode_image_path.split("/")
            j = h[0:-1]
            mnode_image_path = "/".join(j)

			# Checking if use slices
            if mnode.parm("use_slices").eval() == 0:
                render_type = "render_normal"
            elif mnode.parm("use_slices").eval() == 1: #and mnode.parm("vm_tile_render") == 0:
                render_type = "slices"

			# Checking if the camera is stereo.
            camera = mnode.parm("camera").eval()
            camera = hou.node(camera)
            #check the camera does exist in the scene.
            if camera != None:
                #PRINT and error if there is no camera or pointing to a non existing camera
                if camera.type().nameComponents()[2] == "rfxCamera" or camera.type().nameComponents()[2] ==  "rfxAbcCamera":
                    stereo_render = ".%v"
                elif camera.type().nameComponents()[2] == "cam":
                    if "right" in camera.name() or "left" in camera.name():
                        stereo_render = ".%v"
                    else:
                        stereo_render = ""
                else:
                    "print Verify Cameras in Mantra Output, is not Valid Pipeline Camera"
                    #raise and error here
            else:
                raise StandardError

			#checking the file extension
            file_ext = mnode.parm("vm_device").eval()
            if   file_ext == "OpenEXR":
                file_ext = "exr"
            elif file_ext == "Houdini":
                file_ext = "pic"
            elif file_ext == "TIFF":
                file_ext = "tiff"
            elif file_ext == "PNG":
                file_ext = "png"
            elif file_ext == "JPEG":
                file_ext = "jpeg"
            elif file_ext == "RAT":
                file_ext = "rat"
            elif file_ext == "TGA":
                file_ext = "tga"

			# checking if  is using Dtex
            if mnode.parm("vm_deepresolver").eval() == "camera":
                dtex = "dtex_True"
            else:
                dtex = "dtex_False"
			#start end frame
            frame_start = mnode.parm("f1").eval()
            frame_end = mnode.parm("f2").eval()
            frame_interval = mnode.parm("f3").eval()

			#camera_resolution
            camera_resolution = camera.parmTuple("res").eval()

			#Appending the attributes of the rfxmantra to de lists
            list_attributes.append(mnode.parm("namespace").eval())
            list_attributes.append(render_type)
            list_attributes.append(stereo_render)
            list_attributes.append(mnode_image_path)
            list_attributes.append(file_ext)
            list_attributes.append(dtex)
            list_attributes.append(frame_start)
            list_attributes.append(frame_end)
            list_attributes.append(frame_interval)
            list_attributes.append(camera_resolution)

            dict_list.append(list_attributes)

			
			
			
#Writing the PYTHON CODE for the nuke temp script

        file.write("list_nodes = " + str(dict_list)+"\n")
        file.write("""

import os
import sys
import re
import nuke
import nukescripts

nukescripts.stereo.setViewsForStereo()

def format_node(node, res):
    print res
    node.knob('type').setValue('to box')
    #node.knob('box_fixed').setValue(True)
    node.knob('box_width').setValue(res[0])
    node.knob('box_height').setValue(res[1])
    #node.knob('box_pixel_aspect').setValue(res[2])

#Global variables to set the path of the writes out of the slices----------------------------------------------------------
main_path = ''
element = ''
last_path = ''
file_ext = ''
version = ''
slice_info = ''
file_ext = ''

def path_of_dtex(n_node):
    original_path = n_node.knob('file').value()
    path_list = original_path.split('/')
    if 'slice' in original_path:
      global element
      element = path_list[-5]
      el = path_list[-4]
      global main_path
      main_path = path_list[0:8]
      main_path= '/'.join(main_path)
      global version
      version = path_list[-3]
      global slice_info
      slice_info = path_list[-2]
      global info_stereo_frame
      info_stereo_frame = path_list[-1]
      global file_ext
      file_ext = path_list[-1]

      new_path = main_path + '/fx/wip/houdini/'+element+'/renderCache/maps/dtex/'+el+'/'+version +'/'+slice_info +'/'+ info_stereo_frame
      new_path = new_path.replace('.exr','.dtex')
      print new_path
    else:
      global element
      element = path_list[-4]
      global main_path
      main_path = path_list[0:8]
      main_path= '/'.join(main_path)

      version = path_list[13]
      print version

      global last_path
      last_path = path_list[-3:-1]
      last_path = '/'.join(last_path)
      global file_ext
      file_ext = path_list[-1]
      new_path = main_path + '/fx/wip/houdini/'+element+'/renderCache/maps/dtex/'+last_path+'/'+file_ext
      new_path = new_path.replace('.exr','.dtex')
    return new_path

def deepReadNode(n_node):
    new_path = path_of_dtex(n_node)
    opositionX = n_node.knob('xpos').value()
    opositionY = n_node.knob('ypos').value()

    dr =nuke.nodes.DeepRead()
    dr.knob('file').setValue(new_path)
    dr.knob('first').setValue(n_node.knob('first').value())
    dr.knob('last').setValue(n_node.knob('last').value())
    dr['xpos'].setValue(opositionX+100)
    dr['ypos'].setValue(opositionY-15)
    return dr

#n_node is the write node from where is going to get the information, i  is where is going to plug the deepReColor to---------------------------------
def node_to_dtex(n_node,i):
    dr = deepReadNode(n_node)
    deep_reformat = nuke.nodes.DeepReformat()
    format_node(deep_reformat, res)
    deep_reformat.setInput(0,dr)
    deep_trans = nuke.nodes.DeepTransform()
    deep_trans.knob('zscale').setValue(0.01)
    deep_trans.setInput(0, deep_reformat)
    DeepRecolor = nuke.nodes.DeepRecolor()
    DeepRecolor.setInput(1,i)
    DeepRecolor.setInput(0,deep_trans)
    DeepRecolor.knob('targetInputAlpha').setValue(True)
    nukescripts.clear_selection_recursive()
    return DeepRecolor

#looping each Key of the dictionary of mantra nodes.---------------------------------------

# value 0 is mantra node name
# value 1 is render_normal or sliced
# value 2 is stereo or single eye
# value 3 is render path
# value 4 is the file extension
# value 5 if dtex are going to be use
# value 6 frame_start
# value 7 frame_end
# value 8 frame_interval
# value 9 camera resolution (list)

how_many_sliced = 0
n_counter = -1
for i in list_nodes:
    n_counter = n_counter + 1
    nukescripts.clear_selection_recursive()

    if i[1] == 'slices':
        slice_folder = i[3].split('/')
        slice_folder = slice_folder[0:-1]
        slice_folder ='/'.join(slice_folder)
        list_of_slices = os.listdir(slice_folder)
        list_of_slices.sort()

        all_merge = nuke.nodes.Merge()
        if i[5] == 'dtex_True':
            all_deep_merge = nuke.nodes.DeepMerge()

        for index, j in enumerate(list_of_slices):
            if j.startswith('slice'):
                slice_image_path = slice_folder + '/' + j +'/'+i[0] +i[2]+ '.####.'+i[4]

                reader = nuke.nodes.Read()
                reader.knob('file').setValue(slice_image_path)
                reader.knob('first').setValue(int(i[6]))
                reader.knob('last').setValue(int(i[7]))

                reformat = nuke.nodes.Reformat()
                format_node(reformat, i[9])
                reformat.setInput(0,reader)

                all_merge.setInput(index,reformat)

                if i[5] == 'dtex_True':
                    reader.knob('selected').setValue(True)
                    dr = deepReadNode(reader)
                    all_deep_merge.setInput(index, dr)

#end loop of slices --------------------------------------------------------------------

        how_many_sliced = how_many_sliced + 1
        write_slice = nuke.nodes.Write()
        write_slice.knob('render_order').setValue(how_many_sliced)

        write_slice_path = slice_folder + '/merged_slices/' + i[0] + i[2] + '.####.' +i[4]
        print write_slice_path
        write_slice.knob('file').setValue(write_slice_path)
        write_slice.knob('channels').setValue('all')
        write_slice.setInput(0,all_merge)

        if i[5] == 'dtex_True':
            deep_write = nuke.nodes.DeepWrite()
            new_out_path = main_path + '/fx/wip/houdini/'+element+'/renderCache/maps/dtex/'+ i[0]+'/'+version+'/merged_slice/'+file_ext
            new_out_path = new_out_path.replace('.exr','.dtex')
            deep_write.knob('file').setValue(new_out_path)
            deep_write.setInput(0,all_deep_merge)

            deep_write.knob('tile_color').setValue(  4294902015  ) #almost the same yellow as the regular write.
            how_many_sliced = how_many_sliced +1
deep_write.knob('render_order').setValue(how_many_sliced)


            deepReColorNode = nuke.nodes.DeepRecolor()
            deepReColorNode.setInput(1,write_slice)
            deepReColorNode.setInput(0,deep_write)

        null = nuke.nodes.NoOp()
        if i[5] == 'dtex_True':
            null.setInput(0,deepReColorNode)
        else:
            null.setInput(0,write_slice)
        merger = null

#------------------------------------------------------------------------------------------------------------------------------------------------------------
    elif i[1] == 'render_normal':
        reader = nuke.nodes.Read()
reader.knob('file').setValue(i[3]+"/"+i[0]+i[2]+'.'+'####'+'.'+i[4] )
        reader.knob('first').setValue(int(i[6]))
        reader.knob('last').setValue(int(i[7]))

        reformat = nuke.nodes.Reformat()
        print i[9]
        format_node(reformat, i[9])
        reformat.setInput(0,reader)

        if i[5] == 'dtex_False':
            merger = reformat
        elif i[5] == 'dtex_True':
            deepColor = node_to_dtex(reader,reformat)
            merger = deepColor

# HERE IS WHERE THE MAGIC HAPPEN for main loop-------------------------------------------------------------
    if i[5] == 'dtex_True':
        composite = nuke.nodes.DeepMerge()
    elif i[5] == 'dtex_False':
        composite = nuke.nodes.Merge()
        composite.knob('also_merge').setValue('all')
    composite.knob('tile_color').setValue(4399595)

    composite.setInput(0, merger)
    try:
        composite.setInput(1,temp_comp)
    except:
        pass
    temp_file = merger
    temp_comp = composite

    if n_counter == 0:
        merger_spec = temp_comp
        merger_spec.knob('tile_color').setValue(7777795)

## we take the value of the last loop  and use it to set up the write node at the end------------------------------
    last_dtex = i[5]
    last_stereo = i[2]

#AFER LOOP------------------------------------------------------------
nuke.delete(merger_spec)

write_final = nuke.nodes.Write()
write_final.knob('name').setValue('Write_Final')
write_final.knob('note_font_size').setValue(50)
how_many_sliced = how_many_sliced + 1
write_final.knob('render_order').setValue(how_many_sliced)

if last_dtex ==   'dtex_True':
    deep_to_image = nuke.nodes.DeepToImage()
    try:
        deep_to_image.setInput(0,temp_comp)
    except:
        deep_to_image.setInput(0,merger)

    write_final.setInput(0,deep_to_image)

elif last_dtex == 'dtex_False':
    # in case we are using just one node, try to connect to temp comp, if you cant just use reformat
    try:
        write_final.setInput(0, temp_comp)
    except:
        write_final.setInput(0, reformat)
write_final.knob('selected').setValue(True)

path_for_images = os.environ['WIP_RENDER_DIR'] + '/pre_comp_nuke/images/pre_comp_nuke%s.####.exr'%(last_stereo)
write_final.knob('file').setValue(path_for_images)
write_final.knob('channels').setValue('all')
        """)
        if self.platesCheckBox.isChecked():
            print "self.platesCheckBox isChecked"
            file.write("""
try:

# ALL THIS  is for getting the path of the comp that are in the live folder-------------------------------------------
    path_for_plates = os.environ['RFX_HOUDINI_IMAGES'] + '/comp/'
    path_for_live = path_for_plates + 'live/'

# to get the name of the comp file and the latest version we grab a list of folders, and check whos has the max number------------------------
    list_of_folders = os.listdir(path_for_plates)
    print list_of_folders
    try: # maybe live doesn't exist when creating this file-----------------------------------------------------------
        list_of_folders.remove('live')
    except:
        pass
    l_version = max(list_of_folders)
    print l_version

#testing to see if its stereo or not-----------------------------------------------------
    path_for_plate_reader = path_for_live
    print path_for_plate_reader + 'this is path_for_plate_reader'

    list_of_files = os.listdir(path_for_plate_reader)
    print list_of_files

    checker = list_of_files.pop(0)
    print checker

    if '_l' or '_r' in checker:
        path_for_plate_reader = path_for_live + l_version + '_%v.####.dpx'
        print 'the comp is in stereo'
    else:
        path_for_plate_reader = path_for_live + l_version + '.####.dpx'
        print 'the comp is single eye'
    print 'aaaa'

    plate_reader = nuke.nodes.Read()
    plate_reader.knob('file').setValue(path_for_plate_reader)
    print 'setting up the frame range'
    plate_reader.knob('first').setValue(int(frame_start))
    plate_reader.knob('last').setValue(int(frame_end))
    print 'finishing up the frame range'

#connecting the final nodes to merge the plate.-----------------------------------------------------------
    print 'a'
    merge_plate = nuke.nodes.Merge()
    print 'b'
    merge_plate.setInput(1,plate_reader)

    try:
        merge_plate.setInput(0,deep_to_image)
    except:
        merge_plate.setInput(0,merger)
    write_final.setInput(0,merge_plate)

except:
    pass

print ''*3
            """)

        file.write("""
#Saving the Nuke file in the network------------------------------------------------------------------------------------

path_save_file = os.environ['WIP_RENDER_DIR'] + '/pre_comp_nuke/'
version = 1

print 'this is the path that suppose to create if doesn't exist.'
print path_save_file

#if the folder doesn't exist at the time, please create one for me-------------------
if not os.path.exists(path_save_file):
    os.makedirs(path_save_file)

file_to_save = path_save_file + 'pre_comp_nuke_v'+ str(version).zfill(3) +'.nk'

#if the file all ready exist please check the maximum number of revision and add one to it.------------------------
if os.path.exists(file_to_save):
    print 'the file all ready exists let me version up'
    last_version = max(os.listdir(path_save_file))

    last_version = last_version.split('.')[0]
    last_version = int(last_version.split('v')[1])

    file_to_save = path_save_file + 'pre_comp_nuke_v'+ str(last_version+1).zfill(3) +'.nk'
    print file_to_save
    print 'this is the file that should save'
    print 'version up'

print file_to_save

#save the file----------------------------
nuke.scriptSave(file_to_save)
        """)

        file.close()







        from app_manager.nuke_executer import NukeExecuter
        from pipe_api.env import get_pipe_context

        pipe_ctx = get_pipe_context()
        #py_script = '/path/to/script.py'
        py_script = "/tmp/pre_comp.py"
        #batch=True   as argumnent will run it on the background and wont open the UI
        #py_args = (some, args, for, your, script)

        #executer = NukeExectuer(pipe_ctx, py_script=py_script, py_args=_)
        executer = NukeExecuter(pipe_ctx, py_script=py_script, batch=True)
        session = executer.execute()
        session.wait() #// wait for Nuke to exit (or don't)



 ## FIX PRINT THE RIGHT NAME IN HOUDINI PYTHON SHELL  grab the max file num of the folder and print it on the houdini python shell
        print os.environ['WIP_RENDER_DIR']
        nuke_path = os.environ['WIP_RENDER_DIR'] + '/pre_comp_nuke/'
        nuke_path = os.path.realpath(nuke_path)
        print "this is nuke path"
        print nuke_path
        nuke_file = max(os.listdir(nuke_path))
        print this is nuke_file
        print nuke_file
        nuke_path = os.path.join(nuke_path, nuke_file)
        print nuke_path
        hou.ui.setStatusMessage("your file is located: {0}".format(nuke_path), hou.severityType.ImportantMessage)



















































    def reset(self):
        print "a"
        reply = QtGui.QMessageBox(self)
        reply.setText("Are you Sure you want to reset to the initial list???")
        reply.addButton(QtGui.QPushButton('Accept'), QtGui.QMessageBox.YesRole)
        reply.addButton(QtGui.QPushButton('Reject'), QtGui.QMessageBox.NoRole)
#using a particular icon set by us.
#        reply.setIconPixmap(QtGui.QPixmap(Down_Icon))
#using a some of the defaults icons that comes for the Message Box
        reply.setIcon(QtGui.QMessageBox.Question)
        ret = reply.exec_();

        print reply.buttonText(0)
#        reply = QtGui.QMessageBox.question(self, "Do you want to reset the UI?", "Beware Reset is permanent", QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
        if reply.buttonText(0) == "Accept":
            print "reset"
    #        self.selected_nodes = hou.selectedNodes()
            self.populate_table(self.selected_nodes)

#            self.list_of_names = self.get_list()
#            self.list_hou_nodes = self.get_list_hou_nodes(self.list_of_names)
        else:
            pass

    def on_click(self):
        row =  self.table.currentRow()
        column = self.table.currentColumn()
        item = self.table.item(row,column)
#        print item.text()
        return row, column

    def runn(self):
        print "runn"
#        hou_nodes_from_ui =
        self.cop_init(self.recreate_hou_nodes_from_ui())

# grab all the names of the houdini nodes and put them into the ui table----------------------
    def populate_table(self, nodes):
        self.table.setRowCount(len(nodes))

        for index, item in enumerate(nodes):
            text = item.path()
            itm = QtGui.QTableWidgetItem(text,1)

            itm.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled )
            self.table.setItem(index,0,itm) #0 its the column

            icon = QtGui.QIcon(Delete_Icon)
            it = QtGui.QTableWidgetItem(icon, "Delete")
            it.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
            self.table.setItem(index, 1, it)

            icon = QtGui.QIcon(Down_Icon)
            it = QtGui.QTableWidgetItem(icon, "Down")
            it.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
            self.table.setItem(index, 2, it)

            icon = QtGui.QIcon(Up_Icon)
            it = QtGui.QTableWidgetItem(icon, "Up")
            it.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
            self.table.setItem(index, 3, it)

    def icon_buttons_def(self):
        row =  self.table.currentRow()
        column = self.table.currentColumn()
        item = self.table.item(row,column)
        #if the column 1 with the delete icon  remove the row
        if column == 1:
            self.table.removeRow(row)
        #if the column 2 with the delete icon  Down,  move the text one row down
        if column == 2:
            try:
                self.item_original = self.table.item(row,0)
                self.item_swap = self.table.item(row+1,0)

                self.item_original_txt = self.table.item(row,0).text()
                self.item_swap_txt = self.table.item(row+1,0).text()

                self.item_swap.setText(self.item_original_txt)
                self.item_original.setText(self.item_swap_txt)
            except:
                pass

        if column == 3:
            try:
                self.item_original = self.table.item(row,0)
                self.item_swap = self.table.item(row-1,0)

                self.item_original_txt = self.table.item(row,0).text()
                self.item_swap_txt = self.table.item(row-1,0).text()

                self.item_swap.setText(self.item_original_txt)
                self.item_original.setText(self.item_swap_txt)
            except:
                pass

#here we recreate the nodes from ui to Houdini nodes
    def recreate_hou_nodes_from_ui(self):
        self.ui_nodes = []
        for row in xrange(0,self.table.rowCount()):
            item = str(self.table.item(row,0).text())
            houdini_node = hou.node( item )
            self.ui_nodes.append(houdini_node)
        print self.ui_nodes
        return self.ui_nodes

 # in case the user need to add more node to the UI list  this will create a the new houdini nodelist  and stack it at the bottom of the UI list-----------
    def add_more_nodes(self):
        add_nodes_list = []
        for i in hou.selectedNodes():
            if i.type().nameComponents()[2]=="rfxMantra":
                add_nodes_list.append(i)

#        add_nodes_list = hou.selectedNodes()
        num_rows =  self.table.rowCount()

# if the nodes to add are all ready in the UI don't re add them to the UI
        hou_nodes_from_ui = self.recreate_hou_nodes_from_ui()

        for i in add_nodes_list:
            if i not in hou_nodes_from_ui:
                print i
                hou_nodes_from_ui.append(i)
# we clean the table and re populate it with the new table.
        self.table.clearContents()
        self.populate_table(hou_nodes_from_ui)


# Create the Precomp in Houdini -----------------------------------------------------------
    def cop_init(self, list_hou_nodes):
        print list_hou_nodes
        self.parent = list_hou_nodes[0].parent()
        original_position = list_hou_nodes[-1].position()
        posX = original_position[0]
        posY = original_position[1]

        cop_network = self.parent.createNode("cop2net")
        cop_network.setName("cop_PreComp"+ "_" + str(self.selected_nodes[-1].name() ),unique_name = True )
        cop_network.setColor( hou.Color((0,1,0)))
        cop_network.setPosition( [posX + 1, posY-1  ] )
        temp_file = None
        temp_comp = None

        for index, item in enumerate(list_hou_nodes):
            image_path = item.parm("vm_picture").eval()

            if item.parm("trange").eval() == 3:
                main_string_path = image_path.split(".")[-2]
            else:
                main_string_path = image_path.split(".")[-3]

            main_string_path = main_string_path.split("/")
            main_string_path.pop()
            main_string_path.pop()
            main_string_path = "/".join(main_string_path)
            version = '`padzero(4,ch("../../'+item.name()+'/version"))`'

            # verify that we are using rfxcamera with stereo or not.
            if hou.node( item.parm("camera").eval() ).type().nameComponents()[2] == "rfxCamera":

                name = item.parm("namespace").eval()+"_l"
            else:
                name = item.parm("namespace").eval()

            extention = image_path.split(".")[-1]

            path_for_images = ""
            #verifing if its static render or not, and base on that creating the path.
            if item.parm("trange").eval() == 3:
                path_for_images = main_string_path + "/v" + version +"/"+ name +     "." + extention
            else:
                path_for_images = main_string_path + "/v" + version +"/"+ name + ".$F4." + extention
            # if slices but not tile
            if item.parm("use_slices").eval()==1: # and item.parm("vm_tile_render")==0:
                #EVALUATE FOR SLICE NODE
                subnet_slice = cop_network.createNode("subnet")
                subnet_slice.setName(item.name()+"_sliced_Node")
                parm_template = subnet_slice.parmTemplateGroup()
                version_parm = hou.IntParmTemplate("version","version",1)
                parm_template.append(version_parm)
                subnet_slice.setParmTemplateGroup(parm_template)
				subnet_slice.parm("version").setExpression("ch('../../" + item.name() +"/version')")

                file_path = item.parm("vm_picture").eval()
                #There is an issue when using slices

                path_of_slices = file_path.split("slice")[0]
                print path_of_slices
                print "this is path_of_slices"
                temp_filee = None
                temp_compp = None
                counter = -1

                for folder in os.listdir(path_of_slices):
                    if folder.startswith("slice"):
                        counter = counter + 1

                        folder_location = os.path.join(path_of_slices,folder)

                        cop_filee = subnet_slice.createNode("file")
                        cop_filee.setName(folder)
						cop_filee.parm("filename1").revertToDefaults()
                        print item.parm("namespace").eval()

                        pos = path_of_slices.split(item.parm("namespace").eval())[0]
                        extention_file = file_path.split(".")[-1]
                        version = '`padzero(4,ch("../version"))`'
                        print pos
                        print "this is pos"

                        # verify that we are using rfxcamera with stereo or not.
                        if hou.node( item.parm("camera").eval() ).type().nameComponents()[2] == "rfxCamera" or hou.node( item.parm("camera").eval() ).type().nameComponents()[2] == "rfxAbcCamera":
                            path_for_images = pos + item.parm("namespace").eval() + "/" + version +"/"+ "slice"+str((counter)) +"/"+item.parm("namespace").eval() +"_l.$F4." + extention_file
                        else:
                            path_for_images = pos + item.parm("namespace").eval() + "/" + version +"/"+ "slice"+str((counter)) +"/"+item.parm("namespace").eval() +".$F4." + extention_file

						cop_filee.parm("filename1").set(path_for_images)

                        compositee = subnet_slice.createNode("composite")
                        compositee.setInput(0,cop_filee,0)
                        try:
                            compositee.setInput(1,temp_compp,0)
                        except:
                            pass
                        temp_filee = cop_filee
                        temp_compp = compositee
                        if counter == 0:
                            compositee.setColor(hou.Color((0,1,0)))
                        elif counter == 1:
                            compositee.setColor(hou.Color((0,1,1)))
                            compositee.inputs()[1].destroy()

                null_Outt = subnet_slice.createNode("null")
                null_Outt.setName("OUT")
				# if the mantra node us slices is check but they are no folder call slices DO SOMETHING complain or mark an error.
                null_Outt.setInput(0,compositee,0)
                null_Outt.setDisplayFlag(1)
                null_Outt.setRenderFlag(1)

                rop_compp = cop_network.createNode("rop_comp")
                rop_compp.setInput(0,subnet_slice,0)
                rop_compp.setName(item.name()+"_ROP")
                rop_compp.parm("f1").setExpression("$FRAME_START")
                rop_compp.parm("f2").setExpression("$FRAME_END")

                version = '`padzero(4,ch("../../'+ item.name() + '/version"))`'

                path_for_rop = pos + item.name() + "/v" + version +"/pre_comp/"+ item.name() +".$F4." + extention_file

                rop_compp.parm("copoutput").set(path_for_rop)
                rop_compp.parm("mkpath").set(1)

                file_compp = cop_network.createNode("file")
                file_compp.parm("filename1").revertToDefaults()
				file_compp.parm("filename1").set(rop_compp.parm("copoutput"))
                file_compp.move([0,-1])

                subnet_IO = cop_network.collapseIntoSubnet([rop_compp,file_compp])
                subnet_IO.setName("Cache_Slices")
                subnet_IO.bypass(1)
                subnet_slice.layoutChildren()

                cop_file = subnet_IO
            else:
                # we create the file nodes.
                cop_file = cop_network.createNode("file")
                cop_file.parm("filename1").revertToDefaults()
                cop_file.parm("filename1").set(path_for_images)

            # we create the composite node.
            composite = cop_network.createNode("composite")
            composite.setInput(0,cop_file,0)

            # here is where the magic happen.  we try to do the second idea (connecting the composite  before exist)  and because the first loop doesn't exist, it jumps to the except
            try:
                composite.setInput(1,temp_comp,0)
            except:
                pass
            temp_file = cop_file
            temp_comp = composite
            # here we are just deleting the extra composite node that we get after the first file
            if index == 0:
                composite.setColor(hou.Color((0,1,0)))
            elif index == 1:
                composite.setColor(hou.Color((0,1,1)))
                composite.inputs()[1].destroy()

        rop_comp = cop_network.createNode("rop_comp")
        rop_comp.setInput(0,composite,0)
        rop_comp.parm("trange").set("normal")
        rop_comp.parm("f1").setExpression("$FSTART")
        rop_comp.parm("f2").setExpression("$FEND")

rop_comp.parm("copoutput").set("$WIP_RENDER_DIR/pre_comp_houdini/pre_comp_houdini.$F4.exr")
        rop_comp.parm("mkpath").set(1)

        cop_network.layoutChildren()

        fileIn = cop_network.createNode("file")
        fileIn.setPosition( [rop_comp.position()[0],rop_comp.position()[1]-1 ])
        fileIn.setColor(hou.Color((0,.5,.5)))
        fileIn.parm("filename1").revertToDefaults()
        fileIn.parm("filename1").set(rop_comp.parm("copoutput") )

        if len(self.selected_nodes) < 2:
            composite.destroy()

app = QtGui.QApplication.instance()
if app is None:
    app = QtGui.QApplication(["houdini"])
dialog = PreComp()
dialog.show()
pyqt_houdini.exec_(app,dialog)