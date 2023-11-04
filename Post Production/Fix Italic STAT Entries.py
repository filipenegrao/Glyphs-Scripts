#MenuTitle: Fix Italic STAT Entries (OTVAR with 2+ axes)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
For every axis, renames normal STAT entries to ‘Regular’ (also makes changes in name table if necessary), and makes them elidable (Flags=2). Typically only necessary in italic OTVAR exports.
"""

import fontTools
from fontTools import ttLib
from AppKit import NSString
from otvarLib import *

if Glyphs.versionNumber < 3.2:
	Message(
		title="Version Error",
		message="This script requires app version 3.2 or later.",
		OKButton=None,
		)
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Report: Fix Italic STAT Entries")

	suffixes = ["ttf"]
	for suffix in ("woff", "woff2"):
		if Glyphs.defaults[f"GXExport{suffix.upper()}"]:
			suffixes.append(suffix)
	print(f"- suffixes: {', '.join(suffixes)}")

	thisFont = Glyphs.font # frontmost font
	currentExportPath = currentOTVarExportPath()
	print(f"- path: {currentExportPath}")

	variableFontSettings = []
	for instance in thisFont.instances:
		if instance.type == INSTANCETYPEVARIABLE:
			variableFontSettings.append(instance)

	if not variableFontSettings:
		variableFontSettings = [None]

	for variableFontExport in variableFontSettings:
		for suffix in suffixes:
			fontpath = NSString.alloc().initWithString_(currentExportPath).stringByAppendingPathComponent_(otVarFileName(thisFont, thisInstance=variableFontExport, suffix=suffix))
			print(f"\nProcessing: {fontpath}...")
			font = ttLib.TTFont(fontpath)
			changesMade = False

			print("\n👾 Scanning name table:")
			nameTable = font["name"]
			regularID = None
			normalID = None
			highestID = 0
			for entry in nameTable.names:
				currentID = entry.nameID
				if regularID == None and str(entry) == "Regular":
					regularID = currentID
				elif normalID == None and str(entry) == "Normal":
					normalID = currentID
				if currentID > highestID:
					highestID = currentID
			if regularID == None:
				if normalID == None:
					nameTable.addName("Regular", platforms=((3, 1, 1033),), minNameID=highestID)
					regularID = highestID + 1
					print(f"📛 Adding name ID {regularID} ‘Regular’.")
				else:
					nameTable.setName("Regular", normalID, 3, 1, 1033)
					regularID = normalID
					print(f"📛 Overwriting existing name ID {regularID} ‘Normal’ → ‘Regular’.")
				changesMade = True
			else:
				print(f"📛 Found existing nameID {regularID} ‘Regular’. No changes necessary in name table.")
			# regularEntry = nameTable.getName(regularID, 3, 1, langID=1033)
	
			print("\n👾 Scanning STAT table:")
			statTable = font["STAT"].table
			axes = []
			for axisIndex, axis in enumerate(statTable.DesignAxisRecord.Axis):
				axes.append(axis.AxisTag)
			for statIndex, statEntry in enumerate(statTable.AxisValueArray.AxisValue):
				axisTag = axes[statEntry.AxisIndex]
				if statEntry.Format == 2:
					axisValue = statEntry.NominalValue
				else:
					axisValue = statEntry.Value
				isNormalWdth = axisTag=="wdth" and axisValue==100
				isNormalWght = axisTag=="wght" and axisValue==400
				isNormalOtherAxis = axisValue==0 and not axisTag in ("wght", "wdth")
				if isNormalWdth or isNormalWght or isNormalOtherAxis:
					oldNameID = statEntry.ValueNameID
					oldName = nameTable.getName(oldNameID, 3, 1)
					oldFlags = statEntry.Flags
					print(f"🏛️ STAT axis value {statIndex}, {axisTag}={axisValue}: name ID {oldNameID} ‘{oldName}’ → {regularID} ‘Regular’; flags {oldFlags} → 2 (elidable)")
					if oldNameID != regularID:
						changesMade = True
						statEntry.ValueNameID = regularID
					if oldFlags != 2:
						changesMade = True
						statEntry.Flags = 2
	
			if changesMade:
				font.save(fontpath, reorderTables=False)
				print(f"\n💾 Saved {fontpath}\n")
			else:
				print(f"\n🤷🏻‍♀️ No changes made. File left unchanged.")
	
