# -*- coding: utf-8 -*-
"""
python3 fixstat.py -h     ... help
python3 fixstat.py *.ttf  ... apply to all TTFs in current dir
"""

from fontTools import ttLib
from argparse import ArgumentParser
parser = ArgumentParser(
	description="For every axis, renames normal STAT entries to ‘Regular’ (also makes changes in name table if necessary), and makes them elidable (Flags=2). Typically only necessary in italic OTVAR exports with 2 or more axes. Also, fixes Format1/3 duplicates (if a Format 3 exists, there must be no equivalent Format 1 entry)."
)

parser.add_argument(
	"fonts",
	nargs="+",  # one or more font names, e.g. *.otf
	metavar="font",
	help="Any number of OTF or TTF files.",
)


def fixDuplicatesFormat1and3(axes, statTable, changesMade=False):
	# remove format 1 if format 3 exists:
	# collect format 3:
	axisValueArray = statTable.AxisValueArray
	format3entries = []
	for statEntry in axisValueArray.AxisValue:
		if statEntry.Format == 3:
			axisTag = axes[statEntry.AxisIndex]
			axisValue = statEntry.Value
			format3entries.append((axisTag, axisValue))

	# go again and delete format 1 entries with same values:
	if format3entries:
		newAxisValues = []  # ttLib.tables.otTables.AxisValueArray()
		for statEntry in statTable.AxisValueArray.AxisValue:
			axisTag = axes[statEntry.AxisIndex]
			if statEntry.Format == 1:
				axisTag = axes[statEntry.AxisIndex]
				axisValue = statEntry.Value
				# actually we rebuild the table without the Format 1 entries
				# because we cannot directly delete out of a table (or did I miss something?)
				if (axisTag, axisValue) in format3entries:
					print(f"⛔️ Deleting Format 1 entry {axisTag}={axisValue} because equivalent Format 3 exists.")
					changesMade = True
				else:
					# add Format 1 only if it is not represented as Format 3 already
					newAxisValues.append(statEntry)
			else:
				# add all other Formats
				newAxisValues.append(statEntry)
		axisValueArray.AxisValue = newAxisValues

	return changesMade


def fixstat(font):
	changesMade = False
	print("👾 Scanning name table:")
	nameTable = font["name"]
	regularID = None
	normalID = None
	highestID = 0
	for entry in nameTable.names:
		currentID = entry.nameID
		if regularID is None and str(entry) == "Regular":
			regularID = currentID
		elif normalID is None and str(entry) == "Normal":
			normalID = currentID
		if currentID > highestID:
			highestID = currentID
	if regularID is None:
		if normalID is None:
			nameTable.addName("Regular", platforms=((3, 1, 1033), ), minNameID=highestID)
			regularID = highestID + 1
			print(f"  📛 Adding name ID {regularID} ‘Regular’.")
		else:
			nameTable.setName("Regular", normalID, 3, 1, 1033)
			regularID = normalID
			print(f"  📛 Overwriting existing name ID {regularID} ‘Normal’ → ‘Regular’.")
		changesMade = True
	else:
		print(f"  📛 Found existing nameID {regularID} ‘Regular’. No changes necessary in name table.")
	# regularEntry = nameTable.getName(regularID, 3, 1, langID=1033)

	print("👾 Scanning STAT table:")
	statTable = font["STAT"].table

	# collect axes:
	axes = []
	for axisIndex, axis in enumerate(statTable.DesignAxisRecord.Axis):
		axes.append(axis.AxisTag)

	# go through axis values, fix "Regular" naming and elidable flags:
	for statIndex, statEntry in enumerate(statTable.AxisValueArray.AxisValue):
		axisTag = axes[statEntry.AxisIndex]
		if statEntry.Format == 2:
			axisValue = statEntry.NominalValue
		else:
			axisValue = statEntry.Value
		isNormalWdth = axisTag == "wdth" and axisValue == 100
		isNormalWght = axisTag == "wght" and axisValue == 400
		isNormalOtherAxis = axisValue == 0 and axisTag not in ("wght", "wdth")
		if isNormalWdth or isNormalWght or isNormalOtherAxis:
			oldNameID = statEntry.ValueNameID
			oldName = nameTable.getName(oldNameID, 3, 1)
			oldFlags = statEntry.Flags
			print(f"  🏛️ STAT axis value {statIndex}, {axisTag}={axisValue}: name ID {oldNameID} ‘{oldName}’ → {regularID} ‘Regular’; flags {oldFlags} → 2 (elidable)")
			if oldNameID != regularID:
				changesMade = True
				statEntry.ValueNameID = regularID
			if oldFlags != 2:
				changesMade = True
				statEntry.Flags = 2

	changesMade = fixDuplicatesFormat1and3(axes, statTable, changesMade)
	return changesMade


arguments = parser.parse_args()
fonts = arguments.fonts
changed = 0
for i, fontpath in enumerate(fonts):
	print(f"\n📄 {i+1}. Fixing STAT: {fontpath}")
	font = ttLib.TTFont(fontpath)
	changesMade = fixstat(font)
	if changesMade:
		changed += 1
		font.save(fontpath, reorderTables=False)
		print(f"💾 Saved {fontpath}")
	else:
		print("🤷🏻‍♀️ No changes made. File left unchanged.")

print(f"\n✅ Done. Changed {changed} of {i + 1} fonts.\n")
