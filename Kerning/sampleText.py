# -*- coding: utf-8 -*-
from __future__ import print_function
from GlyphsApp import Glyphs
from AppKit import NSNotFound, NSClassFromString
from collections import OrderedDict

def chooseSampleTextSelection(categoryIndex=0, entryIndex=0):
	if Glyphs.versionNumber >= 3:
		# set sample text selection, open tab with first kern string:
		sharedManager = NSClassFromString("GSSampleTextController").sharedManager()
		if not sharedManager.sampleTextCategoryController():
			# quickly open and close the window to initialise the category and entry controllers
			sharedManager.showSampleTextDialog()
			sharedManager.window().close()
		sharedManager.sampleTextCategoryController().setSelectionIndex_(categoryIndex)
		sharedManager.sampleTextEntryController().setSelectionIndex_(0)
	else:
		tab = Glyphs.font.currentTab
		if tab:
			tab.selectSampleTextArrayController().setSelectionIndex_(entryIndex)

def setSelectSampleTextIndex( thisFont, tab=None, marker="### CUSTOM KERN STRING ###"):
	if Glyphs.versionNumber >= 3:
		# Glyphs 3 code
		sampleTexts = OrderedDict([(d['name'], d['text']) for d in Glyphs.defaults["SampleTextsList"]])

		foundSampleString = False
		for sampleTextIndex, k in enumerate(sampleTexts.keys()): # step through the categories until we find our marker
			if marker in k:
				foundSampleString = True
				if not tab:
					tab = thisFont.currentTab
					if not tab:
						tab = thisFont.newTab()
				
				chooseSampleTextSelection(categoryIndex=sampleTextIndex)
				
				# open tab with first kern string:
				#tab.text = sampleTexts[k].splitlines()[0]
				break

		if not foundSampleString:
			print("Warning: Could not find '%s' in sample strings." % marker)
	else:
		# Glyphs 2 code
		sampleTexts = tuple(Glyphs.defaults["SampleTexts"])

		sampleTextIndex = sampleTexts.index(marker)
		if sampleTextIndex > -1:
			if not tab:
				tab = thisFont.currentTab
				if not tab:
					tab = thisFont.newTab()
			chooseSampleTextSelection(entryIndex=sampleTextIndex+1)
			tab.text = sampleTexts[sampleTextIndex+1]
		else:
			print("Warning: Could not find '%s' in sample strings." % marker)

def addToSampleText( kernStrings, marker="### CUSTOM KERN STRING ###"):
	if kernStrings is None:
		print("No kern strings generated.")
		return False
	else:
		# Get current sample texts:
		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			
			kernStringLines = "\n".join(kernStrings)
			newKernStringEntry = dict( name=marker, text=kernStringLines )
			sampleTexts = Glyphs.defaults["SampleTextsList"].mutableCopy()

			# clear old kern strings with same marker:
			indexesToRemove = []
			for index, sampleTextEntry in enumerate(sampleTexts):
				if sampleTextEntry["name"] == marker: # there could be multiple ones
					indexesToRemove.append(index)
			for index in reversed(indexesToRemove):
				sampleTexts.removeObjectAtIndex_(index)
			
			# build new kern string entry :
			sampleTexts.append(newKernStringEntry)
			
			Glyphs.defaults["SampleTextsList"] = sampleTexts
			return True
		else:
			# Glyphs 2 code
			# Get current sample texts:
			sampleTexts = Glyphs.defaults["SampleTexts"].mutableCopy()
		
			# Cut off after marker text:
			i = sampleTexts.indexOfObject_(marker)
			if i == NSNotFound:
				print("Warning: Could not find this marker:\n%s\nAppending it..." % marker)
				sampleTexts.append(marker)
			else:
				sampleTexts = sampleTexts[:i+1]
		
			# Add new kern strings to the list:
			if len(kernStrings) > 0:
				sampleTexts.extend(kernStrings)
			else:
				return False
		
			# Exchange the stored Sample Texts with the new ones:
			Glyphs.defaults["SampleTexts"] = sampleTexts
			return True

def buildKernStrings( listOfLeftGlyphNames, listOfRightGlyphNames, thisFont=None, linePrefix="nonn", linePostfix="noon", mirrorPair=False):
	"""Takes a list of glyph names and returns a list of kernstrings"""
	if thisFont is None:
		print("No font detected.")
		return None
	else:
		kernStrings = []
	
		# collect left names/groups:
		leftGroups = []
		for leftName in listOfLeftGlyphNames:
		
			# Hardcoded changes to prevent Æ/æ from appearing instead of E/e:
			if leftName == "ae" and thisFont.glyphs["ae"].rightKerningGroup == thisFont.glyphs["e"].rightKerningGroup:
				leftName = "e"
			if leftName == "ae.sc" and thisFont.glyphs["ae.sc"].rightKerningGroup == thisFont.glyphs["e.sc"].rightKerningGroup:
				leftName = "e.sc"
			if leftName == "AE" and thisFont.glyphs["AE"].rightKerningGroup == thisFont.glyphs["E"].rightKerningGroup:
				leftName = "E"
		
			leftGroup = thisFont.glyphs[leftName].rightKerningGroup
			if (leftGroup is not None) and (not leftGroup in leftGroups):
				leftGroups.append( leftGroup )
			
				# collect right names/groups:
				rightGroups = []
				for rightName in listOfRightGlyphNames:
				
					# Hardcoded changes:
					if rightName == "idotless" and thisFont.glyphs["idotless"].leftKerningGroup == thisFont.glyphs["n"].leftKerningGroup:
						rightName = "n"
					if rightName == "idotless" and thisFont.glyphs["idotless"].leftKerningGroup == thisFont.glyphs["i"].leftKerningGroup:
						rightName = "i"
					if rightName == "jdotless" and thisFont.glyphs["jdotless"].leftKerningGroup == thisFont.glyphs["j"].leftKerningGroup:
						rightName = "j"
					
					rightGroup = thisFont.glyphs[rightName].leftKerningGroup
					if (rightGroup is not None) and (not rightGroup in rightGroups):
						rightGroups.append( rightGroup )
						if not mirrorPair:
							kernString = "%s/%s/%s %s" % ( linePrefix, leftName, rightName, linePostfix )
						else:
							kernString = "%s/%s/%s/%s %s" % ( linePrefix, leftName, rightName, leftName, linePrefix )
						kernStrings += [ kernString ]
		return kernStrings

def executeAndReport( kernStrings ):
	# brings macro window to front and clears its log:
	# Glyphs.clearLog()
	# Glyphs.showMacroWindow()
	
	# print status and modify Sample Texts:
	print("Adding %i lines to Sample Texts..." % len( kernStrings ))
	if Glyphs.versionNumber >= 3:
		addedKernStings = addToSampleText( kernStrings, marker="Sample String Maker" )
	else:
		addedKernStings = addToSampleText( kernStrings )
	if not addedKernStings:
		print("Warning: could not add the lines.")
	else:
		print("Done.")
	
