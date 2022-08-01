#MenuTitle: Guides through All Selected Nodes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Creates guides through all selected nodes.
"""

from Foundation import NSPoint
import math

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def angle( firstPoint, secondPoint ):
	"""
	Returns the angle (in degrees) of the straight line between firstPoint and secondPoint,
	0 degrees being the second point to the right of first point.
	firstPoint, secondPoint: must be NSPoint or GSNode
	"""
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return math.degrees(math.atan2(yDiff,xDiff))

def newGuide( position, angle=0 ):
	try:
		# GLYPHS 3
		newGuide = GSGuide()
	except:
		# GLYPHS 2
		newGuide = GSGuideLine()
	newGuide.position = position
	newGuide.angle = angle
	return newGuide

def isThereAlreadyAGuideWithTheseProperties(thisLayer,guideposition,guideangle):
	if guideangle < 0:
		guideangle += 180
	if guideangle > 180:
		guideangle -= 180
	for thisGuide in thisLayer.guides:
		thisAngle = thisGuide.angle
		if thisAngle < 0:
			thisAngle += 180
		if thisAngle > 180:
			thisAngle -= 180
		if abs(thisAngle - guideangle) < 0.01 and abs(thisGuide.position.x - guideposition.x) < 0.01 and abs(thisGuide.position.y - guideposition.y) < 0.01:
			return True
	return False

if len(selectedLayers) == 1:
	thisLayer = selectedLayers[0]
	thisGlyph = thisLayer.parent
	currentPointSelection = [point.position for point in thisLayer.selection if type(point) in (GSNode,GSAnchor)]
	
	# thisGlyph.beginUndo() # undo grouping causes crashes
	try:
		if len(currentPointSelection) > 1:
			# clear selection:
			thisLayer.clearSelection()
			currentPointSelection.append(currentPointSelection[0])
			for i,j in enumerate(range(1,len(currentPointSelection))):
				point1 = currentPointSelection[i]
				point2 = currentPointSelection[j]
				angleBetweenPoints = angle(point1,point2)
				middlePoint = addPoints(point1,point2)
				middlePoint.x *= 0.5
				middlePoint.y *= 0.5
			
				# create guide and add it to layer:
				if not isThereAlreadyAGuideWithTheseProperties(thisLayer, middlePoint, angleBetweenPoints):
					guideBetweenPoints = newGuide(middlePoint, angleBetweenPoints)
					thisLayer.guides.append( guideBetweenPoints )
			
				# select it:
				thisLayer.selection.append(guideBetweenPoints)
				
		elif len(currentPointSelection) == 1:
			point = currentPointSelection[0]
			guide = newGuide(point)
			thisLayer.guides.append(guide)

			# select only guide:
			thisLayer.clearSelection()
			thisLayer.selection.append(guide)
				
	except Exception as e:
		raise e
	# finally:
		# thisGlyph.endUndo() # undo grouping causes crashes
			
