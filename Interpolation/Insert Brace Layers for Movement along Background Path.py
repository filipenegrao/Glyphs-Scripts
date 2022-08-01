#MenuTitle: Insert Brace Layers for Movement along Background Path
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Add a single path in the background and it will be used to create intermediate (brace) layers on the first axis for OTVar animation. Define the frames (per segment) in the respective glyph note after running the script once.
"""

from Foundation import NSPoint, NSAffineTransform, NSAffineTransformStruct
import math
from vanilla.dialogs import message
thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs


def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct() # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX,shiftY)
	if skew:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(skew))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		myTransform.appendTransform_(skewTransform)
	return myTransform

def shiftedLayer( originalLayer, shiftTransform ):
	shiftedLayer = originalLayer.copy()
	shiftedLayer.applyTransform( shiftTransform )
	return shiftedLayer

def bezier( P1,  P2,  P3,  P4,  t ):
	"""
	Returns coordinates for t (=0.0...1.0) on curve segment.
	x1,y1 and x4,y4: coordinates of on-curve nodes
	x2,y2 and x3,y3: coordinates of BCPs
	"""
	
	x1, y1 = P1.x, P1.y
	x2, y2 = P2.x, P2.y
	x3, y3 = P3.x, P3.y
	x4, y4 = P4.x, P4.y
	x = x1*(1-t)**3 + x2*3*t*(1-t)**2 + x3*3*t**2*(1-t) + x4*t**3
	y = y1*(1-t)**3 + y2*3*t*(1-t)**2 + y3*3*t**2*(1-t) + y4*t**3

	return NSPoint(x, y)


def getMasterWeightValue( master):
	if Glyphs.versionNumber >= 3:
		# Glyphs 3 code
		return master.axes[0]
	else:
		# Glyphs 2 code
		return master.weightValue

def process( thisLayer, steps=5 ):
	thisGlyph = thisLayer.parent
	thisFont = thisGlyph.parent
	firstAxisID = None
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		firstAxis = thisFont.axes[0]
		if firstAxis:
			firstAxisID = firstAxis.axisId
	
	for i in range(len(thisGlyph.layers))[::-1]:
		thisLayer = thisGlyph.layers[i]
		if thisLayer.layerId != thisLayer.associatedMasterId:
			del thisGlyph.layers[i]
	
	shifts = []
	if len(thisLayer.background.paths) != 1:
		message(messageText="Master's background layer should have a single path", alertStyle="informational")
		return
	movePath = thisLayer.background.paths[0]
	originPoint = movePath.nodes[0]
	if movePath:
		for thisSegment in movePath.segments:
			# curve segments:
			if len(thisSegment) == 4:
				for i in range(steps):
					if Glyphs.versionNumber >= 3:
						# Glyphs 3 code
						offsetPoint = bezier(
							thisSegment[0],
							thisSegment[1],
							thisSegment[2],
							thisSegment[3],
							i*1.0/steps
						)
					else:
						# Glyphs 2 code
						offsetPoint = bezier(
							thisSegment[0].pointValue(),
							thisSegment[1].pointValue(),
							thisSegment[2].pointValue(),
							thisSegment[3].pointValue(),
							i*1.0/steps
						)
					shiftTransform = transform(
						shiftX = offsetPoint.x-originPoint.x,
						shiftY = offsetPoint.y-originPoint.y
					).transformStruct()
					shifts.append( shiftTransform )
			# line segment:
			elif len(thisSegment) == 2:
				if Glyphs.versionNumber >= 3:
					# Glyphs 3 code
					P1 = thisSegment[0]
					P2 = thisSegment[1]

				else:
					# Glyphs 2 code
					P1 = thisSegment[0].pointValue()
					P2 = thisSegment[1].pointValue()
				for i in range(steps):
					shiftTransform = transform(
						shiftX = (P1.x+i*(P2.x-P1.x)/steps)-originPoint.x,
						shiftY = (P1.y+i*(P2.y-P1.y)/steps)-originPoint.y
					).transformStruct()
					shifts.append( shiftTransform )
		
		# all segments are collected in 'shifts':
		firstMaster = thisLayer.parent.parent.masters[0]
		secondMaster = thisLayer.parent.parent.masters[1]
		firstMasterValue = getMasterWeightValue(firstMaster)
		secondMasterValue = getMasterWeightValue(secondMaster)
		frameCount = len(shifts)
		stepWidth = (secondMasterValue-firstMasterValue)/frameCount
		
		for i in range(1,len(shifts)):
			frameTransform = shifts[i]
			frameValue = firstMasterValue + i * stepWidth
			braceLayer = shiftedLayer( thisLayer, frameTransform )
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				braceLayer.attributes['coordinates'] = {firstAxisID: frameValue}
			else:
				# GLYPHS 2
				braceLayer.name = "{%i}" % frameValue
			thisLayer.parent.layers.append( braceLayer )
			

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Insert Brace Layers for Movement along Background Path:\n")
	stepMarker = "Frames"
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		steps = 5
		if thisGlyph.note and stepMarker in thisGlyph.note:
			for lineInNote in thisGlyph.note.splitlines():
				if lineInNote.startswith(stepMarker):
					try:
						steps = int(lineInNote.split()[1])
					except:
						print("⚠️ %s: could not parse glyph note ‘%s’" % (thisGlyph.name, lineInNote.strip()))
		else:
			thisGlyph.note = "%s: %i (per path segment)\n%s" % (stepMarker, steps, thisGlyph.note if thisGlyph.note else "")
		print("🔠 %s: %i frames per background path segment" % (thisGlyph.name, steps))
		# thisGlyph.beginUndo() # undo grouping causes crashes
		process( thisLayer, steps=steps )
		# thisGlyph.endUndo() # undo grouping causes crashes
	
	print("Done.")
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
