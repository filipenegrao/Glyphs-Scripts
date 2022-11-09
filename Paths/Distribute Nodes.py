#MenuTitle: Distribute Nodes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Distributes the selected nodes horizontally or vertically, depending on the bounding box.
"""

Font = Glyphs.font
selectedLayer = Font.selectedLayers[0]

try:
	try:
		# until v2.1:
		selection = selectedLayer.selection()
	except:
		# since v2.2:
		selection = selectedLayer.selection

	selectionXList = [n.x for n in selection]
	selectionYList = [n.y for n in selection]
	leftMostX, rightMostX = min(selectionXList), max(selectionXList)
	lowestY, highestY = min(selectionYList), max(selectionYList)
	diffX = abs(leftMostX - rightMostX)
	diffY = abs(lowestY - highestY)

	Font.disableUpdateInterface()
	try:
		if diffX > diffY:
			increment = diffX / float(len(selection) - 1)
			sortedSelection = sorted(selection, key=lambda n: n.x)
			for thisNodeIndex in range(len(selection) - 1):
				sortedSelection[thisNodeIndex].x = leftMostX + (thisNodeIndex * increment)
		else:
			increment = diffY / float(len(selection) - 1)
			sortedSelection = sorted(selection, key=lambda n: n.y)
			for thisNodeIndex in range(len(selection) - 1):
				sortedSelection[thisNodeIndex].y = lowestY + (thisNodeIndex * increment)
	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Script Error:\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e
	finally:
		Font.enableUpdateInterface() # re-enables UI updates in Font View

except Exception as e:
	if selection == ():
		print("Cannot distribute nodes: nothing selected in frontmost layer.")
	else:
		print("Error. Cannot distribute nodes:", selection)
		print(e)
