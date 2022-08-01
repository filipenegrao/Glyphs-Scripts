#MenuTitle: Transfer Hints to First Master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Moves PostScript (stem and ghost) hints from the current layer to the first master layer, provided the paths are compatible.
"""

from GlyphsApp import TOPGHOST, BOTTOMGHOST, STEM, TTANCHOR, TTSTEM, TTALIGN, TTINTERPOLATE, TTDIAGONAL, TTDELTA

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
firstMaster = thisFont.masters[0]
firstMasterId = firstMaster.id
supportedHintTypes = (TOPGHOST, BOTTOMGHOST, STEM, TTANCHOR, TTSTEM, TTALIGN, TTINTERPOLATE, TTDIAGONAL, TTDELTA, )

def deleteHintsOnLayer(thisLayer):
	for i in range(len(thisLayer.hints))[::-1]:
		if thisLayer.hints[i].type in supportedHintTypes:
			del thisLayer.hints[i]

def transferHintsFromTo( sourceLayer, targetLayer ):
	# clean slate in targetLayer:
	deleteHintsOnLayer(targetLayer)
	sourcePaths = [p for p in sourceLayer.paths]
	targetPaths = [p for p in targetLayer.paths]	
	# go through all hints in source layer:
	for thisHint in sourceLayer.hints:
		
		# if it is a recognized hint type...
		if thisHint.type in supportedHintTypes and thisHint.originNode:
			
			# ... create hint for target layer:
			pathIndex = sourcePaths.index(thisHint.originNode.parent)
			originNodeIndex = thisHint.originNode.index
			newHint = GSHint()
			newHint.type = thisHint.type
			newHint.originNode = targetPaths[pathIndex].nodes[originNodeIndex]
			newHint.horizontal = thisHint.horizontal
			
			# ... look for optional nodes:
			if thisHint.targetNode:
				targetNodeIndex = thisHint.targetNode.index
				targetPathIndex = sourcePaths.index(thisHint.targetNode.parent)
				newHint.targetNode = targetPaths[targetPathIndex].nodes[targetNodeIndex]
				
			if thisHint.otherNode1:
				targetNodeIndex = thisHint.otherNode1.index
				targetPathIndex = sourcePaths.index(thisHint.otherNode1.parent)
				newHint.otherNode1 = targetPaths[targetPathIndex].nodes[targetNodeIndex]
				
			if thisHint.otherNode2:
				targetNodeIndex = thisHint.otherNode2.index
				targetPathIndex = sourcePaths.index(thisHint.otherNode2.parent)
				newHint.otherNode2 = targetPaths[targetPathIndex].nodes[targetNodeIndex]
			
			# ... and add to target layer:
			targetLayer.hints.append(newHint)
		
	# ... delete hints in source layer:
	deleteHintsOnLayer(sourceLayer)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()

	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		if thisLayer.layerId != firstMasterId:
			firstLayer = thisGlyph.layers[firstMasterId]
			if thisGlyph.mastersCompatibleForLayers_([thisLayer,firstLayer]):
				print("Transfering hints in: %s" % thisGlyph.name)
				# thisGlyph.beginUndo() # undo grouping causes crashes
				transferHintsFromTo( thisLayer, firstLayer )
				# thisGlyph.endUndo() # undo grouping causes crashes
			else:
				Glyphs.showMacroWindow()
				print("%s: layers incompatible." % thisGlyph.name)
		else:
			Glyphs.showMacroWindow()
			print("%s: layer '%s' is already the first master layer." % (thisGlyph.name,thisLayer.name))

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
