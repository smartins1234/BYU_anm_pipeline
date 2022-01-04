import nuke
import nukescripts
import os
import glob


def AutoProjectSettings():

	print
	print ('.............................')
	print ('... Starting Auto Project ...')
	print ('.............................')


	#######################
	# Create a Dialog Box #

	# Input variables
	readFile = '/groups/cenote/BYU_anm_pipeline/production/shots/'

	startAt = 'Force Start at Frame 1001'
	exportAt = 'Export at Original Frame Range'
	localizer = 'Localization Policy'
	TCL = 'Use TCL command on Write node'

	saveFolder = '/groups/cenote/'
	scriptName = 'Script Name'
	addFolder = 'scripts, render'


	z = nuke.Panel('New comp from shot layers')

	z.addFilenameSearch('Read File', readFile)
	z.addBooleanCheckBox(startAt,'True')
	z.addBooleanCheckBox(exportAt, 'False')
	z.addBooleanCheckBox(localizer,'False')
	z.addBooleanCheckBox(TCL,'True')
	z.addFilenameSearch('Save Folder', saveFolder)
	z.addSingleLineInput('Script Name', scriptName)
	z.addSingleLineInput('Additional Folders', addFolder)

	z.addButton('Cancel')
	z.addButton('OK')


	z.setWidth(600)
	result = z.show()


	# End of Dialog Box #
	#####################


	if result == 0:
		pass # If hit 'Cancel', pass

	else:

		#files = glob.glob(readFile, recursive=True)
		#print(files)

		# Get values
		readFile = z.value(readFile)

		startAt = z.value(startAt)
		exportAt = z.value(exportAt)
		localizer = z.value(localizer)
		TCL = z.value(TCL)

		saveFolder = z.value(saveFolder)
		scriptName = z.value(scriptName)
		addFolder = z.value('Additional Folders')

		# Internal variables
		createFolder = False
		versionUp = False
		createScriptFolder = False
		createExportFolder = False


		if (readFile == ('Read File')) or (readFile == ('')): # If Read file keep with the original value or is empty, the process will not run
			print ('Nothing to do here!')
			pass

		else:

			task = nuke.ProgressTask( 'Creating script...' )

			if (saveFolder == '') or (saveFolder == 'Master Folder'):
				createFolder = False
				print
				print ('No folder structure created ')

			else:

				###########################
				# Create Folder Structure #


				createFolder = True

				shotFolder = (os.path.join(saveFolder, scriptName))

				print
				print ('Create folder structure at')
				print (saveFolder)

				try:
					os.mkdir(shotFolder)
					print
					print ('-> Shot folder created: ' + shotFolder)
					task.setMessage( 'Creating: %s' % (shotFolder))

				except:
					print
					print ('-> Main folder already exist!\n%s' %(shotFolder))

				if (addFolder == ''):
					#createFolder = False
					print
					print ("--> Don't create any sub-folders")
					pass

				else:

					folderList = []

					for i in addFolder.split(', '):
						folderList.append(i)

					# Create sub-directories
					for i in folderList:
						folderName = (os.path.join(shotFolder, i))
						folderName = folderName.replace('\\', '/')

						task.setMessage( 'Creating: %s' % (folderName))

						try:
							os.mkdir(folderName)
							print
							print ('--> Created sub-directory: ' + folderName)

						except:
							print
							print ('--> Folder already exist!\n%s' %(folderName))
							versionUp = True

						if folderList.index(i) == 0:
							scriptFolder = folderName # Get the first folder name to save the Script
							createScriptFolder = True

						if folderList.index(i) == 1:
							exportFolder = folderName # Get the second folder name to set the Write node
							createExportFolder = True

				print
				print ('++++++++++++++++++++++++++++++++++')


				# End of Folder Creator #
				#####################


			###############
			# Create Read #


			filelist = [readFile]

			if filelist != None:
				for f in filelist:
					newRead = nuke.createNode("Read", "file {" + f + "}", inpanel = True)


			inPoint = newRead['first'].getValue()
			outPoint = newRead['last'].getValue()
			newRead['before'].setValue('black')
			newRead['after'].setValue('black')
			newRead.hideControlPanel()

			inPoint = int(inPoint)
			outPoint = int(outPoint)

			print
			print ('Read Node created: ' + newRead.name())
			print ('--> ' + f)

			task.setMessage( 'Creating: %s' % (newRead.name()))


			if localizer == True:
				newRead['localizationPolicy'].setValue('on')

			# Get Read infos
			width = (newRead.width())
			height = (newRead.height())

			frameRate = (newRead.metadata('input/frame_rate'))

			xPos = newRead['xpos'].getValue()
			yPos = newRead['ypos'].getValue()

			readFormat = newRead.knob('format').value().name()

			redAspect = False

			aspectRatio = (newRead.metadata('exr/pixelAspectRatio'))
			if aspectRatio == None:
				try:
					aspectRatio = (newRead.metadata('r3d/pixel_aspect_ratio'))
					redAspect = True

				except:
					aspectRatio = (newRead.metadata('input/pixel_aspect'))
					print ('Input aspect Ratio')


			# End Create Read #
			###################


			###################
			# Create Timeclip #


			tclip = nuke.createNode('TimeClip')

			tclip['first'].setValue(int(inPoint))
			tclip['last'].setValue(int(outPoint))

			tclip['before'].setValue('black')
			tclip['after'].setValue('black')

			tclip['frame_mode'].setValue('start at')

			print
			print ('Timeclip Node created: ' + tclip.name())

			task.setMessage ( 'Creating: %s' % (tclip.name()))

			if exportAt == True:
				origInPoint = inPoint
				origOutPoint = outPoint

			if startAt == True:
				outPoint = (outPoint - inPoint) + 1001
				inPoint = 1001


			tclip['frame'].setValue(str(inPoint))

			tclip.setInput(0, newRead)

			tclip.hideControlPanel()

			tclip['xpos'].setValue(xPos)
			tclip['ypos'].setValue(yPos + 100)

			tclip['selected'].setValue(False)


			# End Timeclip #
			################

			##############
			# Create Dot #

			nDot = nuke.createNode('Dot')
			nDot['name'].setValue('FinalOutput')
			nDot['label'].setValue('Final Output')

			nDot.setInput(0, tclip)

			nDot.hideControlPanel()

			nDot['xpos'].setValue(xPos + 34)
			nDot['ypos'].setValue(yPos + 650)

			nDot['selected'].setValue(False)

			# End Dot #
			###########


			#################
			# Create Viewer #


			v = 0

			for i in nuke.allNodes():
				if i.Class() in ('Viewer'):
					v = v + 1

			if v == 0:
				nViewer = nuke.createNode('Viewer')
				nViewer.setInput(0, nDot)
				nViewer['xpos'].setValue(xPos + 200)
				nViewer['ypos'].setValue(yPos + 650)
				nViewer['selected'].setValue(False)


			if startAt == True:
				nuke.frame(1001)

			else:
				nuke.frame(int(inPoint))


			# End Viewer #
			##############


			####################################
			# Create Backdrop for Read Session #


			newRead['selected'].setValue(True)

			sel = nuke.selectedNode()

			Xw = sel['xpos'].getValue()
			Yw = sel['ypos'].getValue()

			if exportAt == True:
				rLabel = ('<center><img src = "'"Read.png"'" >Read File\n<font size = 1>Frame Range: %d - %d\nOriginal Frame Range: %d - %d' %((inPoint), (outPoint), int(origInPoint), int(origOutPoint)))

			else:
				rLabel = ('<center><img src = "'"Read.png"'" >Read File\n<font size = 1>Frame Range: %s - %s' %(inPoint, outPoint))

			bk = nukescripts.autoBackdrop()
			bk['label'].setValue(rLabel)
			bk['bdwidth'].setValue( 500 )
			bk['bdheight'].setValue( 500 )
			bk['xpos'].setValue( Xw - 225 )
			bk['ypos'].setValue( Yw - 200 )

			print
			print ('Backdrop created: ' + bk.name())
			print
			print ('++++++++++++++++++++++++++++++++++')

			task.setMessage ( 'Creating: %s' % (bk.name()))


			# End of create Backdrop #
			##########################


			##########################
			# Setup Project Settings #


			print
			print ('Project Settings')

			task.setMessage ( 'Project Settings...' )

			sel = nuke.selectedNode()

			nkRoot = nuke.root()

			if frameRate == None:
				nkRoot['fps'].setValue(24)

			else:
				nkRoot['fps'].setValue(frameRate)


			if aspectRatio == None:
				aspectRatio = 1


			nkRoot['first_frame'].setValue(inPoint)
			nkRoot['last_frame'].setValue(outPoint)
			nkRoot['lock_range'].setValue(True)

			print
			print ('Set Frame Range to %s:%s' % (str(inPoint), str(outPoint)))


			if readFormat == None:
				newFormatName = ('%s_Resolution' %(newRead.name()))
				nuke.addFormat('%d %d %d %s' %(width, height, aspectRatio, newFormatName))
				nkRoot['format'].setValue(newFormatName)
				newRead['format'].setValue(newFormatName)
				print
				print ('Set Format to %s %sx%s, and aspect ratio to %s' % (newFormatName, str(width), str(height), str(aspectRatio)))


			else:
				for each in (nuke.formats()):
					if (each.name()) == readFormat:
						nkRoot['format'].setValue(each.name())
						print
						print ('Set Format to %s %sx%s, and aspect ratio to %s' % (str(each.name()), str(width), str(height), str(aspectRatio)))
						pass


			print
			print ('++++++++++++++++++++++++++++++++++')


			# End of Project Settings #
			###########################


			##################################################
			# Create Timeclip to set to original plate range #

			if exportAt == True:
				newRead['selected'].setValue(False)

				exclip = nuke.createNode('TimeClip')

				exclip['first'].setValue(int(inPoint))
				exclip['last'].setValue(int(outPoint))

				exclip['before'].setValue('black')
				exclip['after'].setValue('black')

				exclip.hideControlPanel()

				exclip['xpos'].setValue(xPos)
				exclip['ypos'].setValue(yPos + 910)

				exclip.setInput(0, nDot)

				exclip['selected'].setValue(False)
				exclip['frame_mode'].setValue('start at')

				exclip['frame'].setValue(str(origInPoint))

				task.setMessage ( 'Creating: %s' % (exclip.name()))

				print
				print ('Timeclip Node created: ' + exclip.name())


			# End Timeclip Reverse #
			########################


			####################
			#Create Write node #


			newRead['selected'].setValue(False)

			nWrite = nuke.createNode('Write')

			nWrite['name'].setValue('Write_Output')
			nWrite['channels'].setValue('rgb')
			nWrite['file_type'].setValue('exr')
			nWrite['create_directories'].setValue(True)

			task.setMessage ( 'Creating: %s' % (nWrite.name()))

			frHash = '####'

			if (createExportFolder == True):
				if TCL == True:
					folderTCL = '[lindex [split [lindex [split [value root.name] /] end] .] 0]'
					scriptTCL = '[lindex [split [lindex [split [value root.name] /] end] .] 0].%05d.exr'
					writeFile = ('%s/%s/%s' %(exportFolder, folderTCL, scriptTCL))

				else:
					writeFile = ('%s/%s_v001/%s_v001.%s.exr' %(exportFolder, scriptName, scriptName, frHash))

				nWrite['file'].setValue(writeFile)



			nWrite['xpos'].setValue(xPos)
			nWrite['ypos'].setValue(yPos + 1000)

			print
			print ('Write Node created: ' + nWrite.name())

			if exportAt == True:
				nWrite.setInput(0, exclip)

			else:
				nWrite.setInput(0, nDot)

			nWrite.hideControlPanel()


			nWrite['selected'].setValue(True)
			sel = nuke.selectedNode()

			Xw = sel['xpos'].getValue()
			Yw = sel['ypos'].getValue()


			# End Write #
			#############


			################################
			#Create Backdrod to Write Area #


			if exportAt == True:
				wLabel = ('<center><img src = "'"Write.png"'" >Output\n<font size = 1>Frame Range: %d - %d\nOriginal Frame Range: %d - %d' % ((inPoint), (outPoint), int(origInPoint), int(origOutPoint)))

			else:
				wLabel = ('<center><img src = "'"Write.png"'" >Output\n<font size = 1>Frame Range: %d - %d' % (inPoint, outPoint))

			bk = nukescripts.autoBackdrop()
			bk['label'].setValue(wLabel)
			bk['bdwidth'].setValue(500)
			bk['bdheight'].setValue(400)
			bk['xpos'].setValue(Xw-225)
			bk['ypos'].setValue(Yw-300)

			task.setMessage ( 'Creating: %s' % (bk.name()))

			print
			print ('Backdrop created: ' + bk.name())
			print
			print ('++++++++++++++++++++++++++++++++++')


			# End Backdrop #
			################


			######################################################
			# Save project at first folder name from user's list #


			message = False
			version = 'v001'

			try:
				path, dirs, files = next(os.walk(scriptFolder))

				if (len(files) >= 1):
					a = len(files) + 1
					version = 'v00' + str(a) + '_avoidOverwrite'
					message = True

			except:
				print
				print ('No script Folder')
				pass

			# Get name from clip
			clipname = os.path.basename(readFile)

			nameList = []

			for a in clipname.split('.'):
			    nameList.append(a)

			newName = nameList[0]

			newName = newName.replace('#', '')


			if (createScriptFolder == True):
				task.setMessage ( 'Saving...')

				if scriptName == '':
					nukeFile = os.path.join(scriptFolder, ('%s_%s.nk' %(newName, version)))

				else:
					nukeFile = os.path.join(scriptFolder, ('%s_%s.nk' %(scriptName, version)))

				nukeFile = nukeFile.replace('\\', '/')

				if (message == True):
					nuke.message('Saved as\n%s\nto avoid overwrite other script!\nPlease, save comp with new name.' % (nukeFile))

				nuke.scriptSaveAs(nukeFile)

				print
				print ('Script saved at: ' + nukeFile)
				print
				print ('++++++++++++++++++++++++++++++++++')
				print


			elif (createFolder == True):
				task.setMessage ( 'Saving...')

				if scriptName == '':
					nukeFile = os.path.join(shotFolder, ('%s_%s.nk' %(newName, version)))

				else:
					nukeFile = os.path.join(shotFolder, ('%s_%s.nk' %(scriptName, version)))

				nukeFile = nukeFile.replace('\\', '/')

				if (message == True):
					nuke.message('Saved as\n%s\nto avoid overwrite other script!\nPlease, save comp with new name.' % (nukeFile))

				nuke.scriptSaveAs(nukeFile)

				print
				print ('Script saved at: ' + nukeFile)
				print
				print ('++++++++++++++++++++++++++++++++++')
				print

			else:
				nuke.message('<font size = "4" color = "red"><center><b>ATENTION!</b></font>\nScript unsaved! Please, do it!')

				print
				print ('######### ATENTION! ##########')
				print ('Script unsaved! Please, do it!')
				print
				print ('++++++++++++++++++++++++++++++++++')
				print

			print ('++++++++++++++++++++++++++++++++++')
			print ('..................................')
			print


			# End Save file #
			#################


def SaveandClose():

	ignoreUnsavedChanges=False

	filename=None

	root = nuke.Root()

	if not ignoreUnsavedChanges and root is not None and root.modified() and len(root.nodes()) > 0:
		runScriptSave = False

		if filename is None:
			scriptName = ''

			try:
				scriptName = nuke.scriptName()

			except RuntimeError:
				scriptName = 'untitled'

			try:
				runScriptSave = nuke.askWithCancel( "Save changes to " + scriptName + " before closing?" )

			except nuke.CancelledError:
				pass

		else:
		    runScriptSave = True

		if runScriptSave:

			try:
				nuke.scriptSave( filename )

			except RuntimeError:
				pass

	nuke.scriptClear()

	AutoProjectSettings()



#Add to menu and assign shortcut key
#nodeMenu = nuke.menu('Nuke').findItem('File')
nodeMenu = nuke.menu('Nuke').addMenu('Cenote')
nodeMenu.addCommand('Cenote Shot Builder', 'SaveandClose()', 'ctrl+shift+r')
