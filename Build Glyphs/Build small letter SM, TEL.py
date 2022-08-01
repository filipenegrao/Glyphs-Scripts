#MenuTitle: Build small letter SM, TEL
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Creates the glyphs: servicemark, telephone.
"""

expansion = 5
newGlyphs = {
	"servicemark": "SM",
	"telephone": "TEL"
}

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

import math

			
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

# def offsetLayer( thisLayer, offset, makeStroke=False, position=0.5, autoStroke=False ):
# 	def _filter(name):
# 		for filter in Glyphs.filters:
# 			if filter.__class__.__name__ == name:
# 				return filter
# 	offsetFilter = _filter("GlyphsFilterOffsetCurve")
# 	lastArg = autoStroke
# 	if not autoStroke:
# 		lastArg = position
# 	else:
# 		lastArg = 1
# 	if makeStroke:
# 		makeStroke = 1
# 	else:
# 		makeStroke = 0
# 	offsetFilter.processLayer_withArguments_(
# 			thisLayer, 
# 			['GlyphsFilterOffsetCurve',f"{offset}", f"{offset}", f"{makeStroke}", f"{lastArg}"]
# 		)

def offsetLayer( thisLayer, offset, makeStroke=False, position=0.5, autoStroke=False ):
	offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
	try:
		# GLYPHS 3:	
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			thisLayer,
			offset, offset, # horizontal and vertical offset
			makeStroke,     # if True, creates a stroke
			autoStroke,     # if True, distorts resulting shape to vertical metrics
			position,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, True )
	except:
		# GLYPHS 2:
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyle_keepCompatibleOutlines_(
			thisLayer,
			offset, offset, # horizontal and vertical offset
			makeStroke,     # if True, creates a stroke
			autoStroke,     # if True, distorts resulting shape to vertical metrics
			position,       # stroke distribution to the left and right, 0.5 = middle
			thisLayer.glyphMetrics(), # metrics (G3)
			None, None, # error, shadow
			0, # NSButtLineCapStyle, # cap style
			True, # keep compatible
			)
		

	

reference = thisFont.glyphs["M"]
trademark = thisFont.glyphs["trademark"]

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisMaster in thisFont.masters:
		tmLayer = trademark.layers[thisMaster.id]
		smallscale = tmLayer.bounds.size.height - 2 * expansion
		largescale = reference.layers[thisMaster.id].bounds.size.height
		scale = smallscale/largescale
		upshift = tmLayer.bounds.origin.y + expansion
	
		measureLayer = tmLayer.copyDecomposedLayer()
		measureLayer.removeOverlap()
		distance = measureLayer.paths[1].bounds.origin.x - (measureLayer.paths[0].bounds.origin.x + measureLayer.paths[0].bounds.size.width) 
	
		for newGlyphName in newGlyphs:
			newGlyph = thisFont.glyphs[newGlyphName]
			if not newGlyph:
				newGlyph = GSGlyph(newGlyphName)
				thisFont.glyphs.append( newGlyph )
		
			newGlyph.leftKerningGroup = trademark.leftKerningGroup
			newGlyph.rightKerningGroup = trademark.rightKerningGroup
			newLayer = newGlyph.layers[thisMaster.id]
			newLayer.clear()
			for i, letter in enumerate(newGlyphs[newGlyphName]):
				letterComp = GSComponent(letter)
				newLayer.components.append(letterComp)
				letterComp.disableAlignment = True
				scaleDown = transform(scale=scale).transformStruct()
				letterComp.applyTransform(scaleDown)
				if i > 0:
					prevComp = newLayer.components[i-1]
					newOrigin = prevComp.bounds.origin.x + prevComp.bounds.size.width + distance + 2*expansion
					currentOrigin = letterComp.bounds.origin.x
					shiftRight = transform(shiftX=(newOrigin-currentOrigin)).transformStruct()
					letterComp.applyTransform(shiftRight)
		
			newLayer.decomposeComponents()
			newLayer.anchors = None
			shiftUp = transform( shiftY=upshift ).transformStruct()
			newLayer.applyTransform( shiftUp )
			offsetLayer( newLayer, expansion )
			newLayer.LSB = tmLayer.LSB
			newLayer.RSB = tmLayer.RSB
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
