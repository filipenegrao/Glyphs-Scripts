# MenuTitle: Fix Arrow Positioning
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Fixes the placement and metrics keys of arrows, dependent on a specified default arrow. Adds metric keys and moves arrows vertically. Does not create new glyphs, only works on existing ones.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject
from mekkablue.geometry import transform


def intersectionsBetweenPoints(thisLayer, startPoint, endPoint):
	"""
	Returns list of intersection NSPoints from startPoint to endPoint.
	thisLayer ... a glyph layer
	startPoint, endPoint ... NSPoints
	"""

	# prepare layer copy for measurement:
	cleanLayer = thisLayer.copyDecomposedLayer()
	cleanLayer.removeOverlap()

	# measure and return tuple:
	listOfIntersections = cleanLayer.intersectionsBetweenPoints(startPoint, endPoint)
	if len(listOfIntersections) % 2 == 1:
		listOfIntersections = cleanLayer.calculateIntersectionsStartPoint_endPoint_decompose_(startPoint, endPoint, True)
	return listOfIntersections


class FixArrowPositioning(mekkaObject):
	prefDict = {
		"referenceForHorizontalArrows": 0,
		"referenceForVerticalArrows": 0,
		"referenceForDiagonalArrows": 0,
		"verticalPosOfHorizontalArrows": 1,
		"verticalPosOfDiagonalArrows": 0,
		"addAndUpdateMetricsKeys": 1,
		"suffix": "",
	}
	hArrows = ("rightArrow", "leftArrow")
	vArrows = ("upArrow", "downArrow", "upDownArrow")
	dArrows = ("northEastArrow", "southEastArrow", "southWestArrow", "northWestArrow")

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 226
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Fix Arrow Positioning",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.explanation = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Fixes position and spacing of arrows.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.referenceForHorizontalArrowsText = vanilla.TextBox((inset, linePos + 2, 130, 14), "Reference for H arrows", sizeStyle='small')
		self.w.referenceForHorizontalArrows = vanilla.PopUpButton((inset + 127, linePos, -inset, 17), self.hArrows, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.referenceForVerticalArrowsText = vanilla.TextBox((inset, linePos + 2, 130, 14), "Reference for V arrows", sizeStyle='small')
		self.w.referenceForVerticalArrows = vanilla.PopUpButton((inset + 127, linePos, -inset, 17), self.vArrows, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.referenceForDiagonalArrowsText = vanilla.TextBox((inset, linePos + 2, 130, 14), "Reference for D arrows", sizeStyle='small')
		self.w.referenceForDiagonalArrows = vanilla.PopUpButton((inset + 127, linePos, -inset, 17), self.dArrows, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.suffixText = vanilla.TextBox((inset, linePos + 2, 70, 14), "Dot suffix", sizeStyle='small', selectable=False)
		self.w.suffix = vanilla.EditText((inset + 58, linePos, -inset, 19), "", sizeStyle='small')
		linePos += lineHeight

		self.w.verticalPosOfHorizontalArrows = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Fix vertical positioning of horizontal arrows", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.verticalPosOfDiagonalArrows = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Fix vertical positioning of diagonal arrows", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.addAndUpdateMetricsKeys = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Add and update metrics keys", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Fix", callback=self.FixArrowPositioningMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def addSuffixIfAny(self, glyphname, suffix):
		suffix = suffix.strip()
		glyphname = glyphname.strip()
		if suffix:
			# add dot if missing:
			suffix = ".%s" % suffix
			suffix = suffix.replace("..", ".")
			glyphname += suffix
		return glyphname

	def measureBottomOfCenterStroke(self, layer):
		extra = 5
		hCenter = (layer.bounds.origin.x + layer.bounds.size.width) * 0.5
		startY = layer.bounds.origin.y - extra
		endY = startY + layer.bounds.size.height + 2 * extra
		startPoint = NSPoint(hCenter, startY)
		endPoint = NSPoint(hCenter, endY)
		measures = intersectionsBetweenPoints(layer, startPoint, endPoint)
		print(layer.parent.name, len(measures), [round(p.y) for p in measures])
		if len(measures) == 8:
			return measures[3].y
		else:
			return measures[1].y

	def updateMetricsKeys(self, thisGlyph):
		thisFont = thisGlyph.font
		if thisFont:
			# update all master layers:
			for thisMaster in thisFont.masters:
				thisLayer = thisGlyph.layers[thisMaster.id]
				thisLayer.updateMetrics()
				thisLayer.syncMetrics()

	def FixArrowPositioningMain(self, sender):
		try:
			# query and update reference and other names:
			hArrowName = self.hArrows[self.pref("referenceForHorizontalArrows")]
			vArrowName = self.vArrows[self.pref("referenceForVerticalArrows")]
			dArrowName = self.dArrows[self.pref("referenceForDiagonalArrows")]

			suffix = self.pref("suffix")
			hArrowName = self.addSuffixIfAny(hArrowName, suffix)
			vArrowName = self.addSuffixIfAny(vArrowName, suffix)
			dArrowName = self.addSuffixIfAny(dArrowName, suffix)

			allHArrowNames = self.hArrows + ("leftRightArrow", )  # add leftRightArrow because it cannot be a reference glyph
			allHorizontalArrowGlyphNames = [self.addSuffixIfAny(name, suffix) for name in allHArrowNames]

			allDiagonalArrowGlyphNames = [self.addSuffixIfAny(name, suffix) for name in self.dArrows]

			# bools for what we should do:
			shouldFixHorizontalArrows = self.prefBool("verticalPosOfHorizontalArrows")
			shouldFixDiagonalArrows = self.prefBool("verticalPosOfDiagonalArrows")
			shouldTakeCareOfMetricsKeys = self.prefBool("addAndUpdateMetricsKeys")

			thisFont = Glyphs.font

			if not Glyphs.font:
				Message(title="Fix Arrow Positioning Error", message="The script requires that a font is open for editing.", OKButton=None)
			else:
				# clears macro window log:
				Glyphs.clearLog()
				warnAboutLayers = []

				# HORIZONTAL ARROWS:
				if shouldFixHorizontalArrows:
					hReferenceGlyph = thisFont.glyphs[hArrowName]
					if not hReferenceGlyph:
						Message(title="Fix Arrow Positioning Error", message=u"No glyph found with name: ‘%s’. Cannot fix horizontal arrows." % hArrowName, OKButton=None)
					else:
						print("\nFIXING VERTICAL POSITIONS OF HORIZONTAL ARROWS:")

						# step through arrow glyphs
						for thisMaster in thisFont.masters:
							referenceHeight = self.measureBottomOfCenterStroke(hReferenceGlyph.layers[thisMaster.id])
							print("\nChecking for master %s..." % thisMaster.name)
							for horizontalArrowName in allHorizontalArrowGlyphNames:
								horizontalArrow = thisFont.glyphs[horizontalArrowName]
								if not horizontalArrow:
									print(u"⚠️ WARNING: no glyph found for '%s'." % horizontalArrowName)
								else:
									# do we need to warn?
									if len(horizontalArrow.layers) > len(thisFont.masters):
										warnAboutLayers.append(horizontalArrowName)

									# measure the layer for the current master:
									horizontalArrowLayer = horizontalArrow.layers[thisMaster.id]
									thisHeight = self.measureBottomOfCenterStroke(horizontalArrowLayer)
									shift = referenceHeight - thisHeight

									# shift if necessary:
									if abs(shift) > 0.6:
										shiftTransformMatrix = transform(shiftY=shift).transformStruct()
										horizontalArrowLayer.applyTransform(shiftTransformMatrix)
										print(u"⚠️ %s: layer '%s' shifted %i units." % (
											horizontalArrow.name,
											horizontalArrowLayer.name,
											shift,
										))
									else:
										print(u"💚 %s: layer '%s' is already OK." % (
											horizontalArrow.name,
											horizontalArrowLayer.name,
										))

				# DIAGONAL METRICS:
				if shouldFixDiagonalArrows:
					dReferenceGlyph = thisFont.glyphs[dArrowName]
					if not dReferenceGlyph:
						Message(title="Fix Arrow Positioning Error", message=u"No glyph found with name: ‘%s’. Cannot fix diagonal arrows." % dArrowName, OKButton=None)
					else:
						print("\nFIXING VERTICAL POSITIONS OF DIAGONAL ARROWS:")

						# step through arrow glyphs
						warnAboutLayers = []
						for thisMaster in thisFont.masters:
							referenceLayer = dReferenceGlyph.layers[thisMaster.id]
							referenceHeight = referenceLayer.bounds.origin.y + referenceLayer.bounds.size.height * 0.5
							print("\nChecking for master %s..." % thisMaster.name)
							for diagonalArrowName in allDiagonalArrowGlyphNames:
								diagonalArrow = thisFont.glyphs[diagonalArrowName]
								if not diagonalArrow:
									print(u"⚠️ WARNING: no glyph found for '%s'." % diagonalArrowName)
								else:
									# do we need to warn?
									if len(diagonalArrow.layers) > len(thisFont.masters):
										warnAboutLayers.append(diagonalArrowName)

									# measure the layer for the current master:
									diagonalArrowLayer = diagonalArrow.layers[thisMaster.id]
									thisHeight = diagonalArrowLayer.bounds.origin.y + diagonalArrowLayer.bounds.size.height * 0.5
									shift = referenceHeight - thisHeight

									# shift if necessary:
									if abs(shift) > 0.6:
										shiftTransformMatrix = transform(shiftY=shift).transformStruct()
										diagonalArrowLayer.applyTransform(shiftTransformMatrix)
										print(u"⚠️ %s: layer '%s' shifted %i units." % (
											diagonalArrow.name,
											diagonalArrowLayer.name,
											shift,
										))
									else:
										print(u"💚 %s: layer '%s' is already OK." % (
											diagonalArrow.name,
											diagonalArrowLayer.name,
										))

				# SET METRICS KEYS ...
				if shouldTakeCareOfMetricsKeys:
					print("\nSETTING METRICS:")

					# ... FOR HORIZONTAL ARROWS:
					if not thisFont.glyphs[hArrowName]:
						print(u"❌ Reference glyph not found: %s. Cannot update metrics for horizontal arrows." % hArrowName)
					else:
						for thisName in allHArrowNames:
							if thisName != hArrowName:
								thisGlyph = thisFont.glyphs[thisName]
								if not thisGlyph:
									print(u"⚠️ Warning: '%s' not found in font." % thisName)
								else:
									if "left" in hArrowName and "left" in thisName.lower():
										thisGlyph.leftMetricsKey = "=%s" % hArrowName
										thisGlyph.rightMetricsKey = "=|%s" % hArrowName
									elif "right" in hArrowName and "right" in thisName.lower():
										thisGlyph.leftMetricsKey = "=|%s" % hArrowName
										thisGlyph.rightMetricsKey = "=%s" % hArrowName
									else:
										thisGlyph.leftMetricsKey = "=|%s" % hArrowName
										thisGlyph.rightMetricsKey = "=|%s" % hArrowName
									self.updateMetricsKeys(thisGlyph)
									print(u"✅ Metrics updated: %s" % thisName)

					# ... FOR DIAGONAL ARROWS:
					if not thisFont.glyphs[dArrowName]:
						print(u"❌ Reference glyph not found: %s. Cannot update metrics for diagonal arrows." % dArrowName)
					else:
						for thisName in self.dArrows:
							if thisName != dArrowName:
								thisGlyph = thisFont.glyphs[thisName]
								if not thisGlyph:
									print(u"⚠️ Warning: '%s' not found in font." % thisName)
								else:
									# northEastArrow, southEastArrow, southWestArrow, northWestArrow:
									if ("East" in dArrowName and "West" in thisName) or ("West" in dArrowName and "East" in thisName):
										thisGlyph.leftMetricsKey = "=|%s" % dArrowName
										thisGlyph.rightMetricsKey = "=|%s" % dArrowName
									else:
										thisGlyph.leftMetricsKey = "=%s" % dArrowName
										thisGlyph.rightMetricsKey = "=%s" % dArrowName
									self.updateMetricsKeys(thisGlyph)
									print(u"✅ Metrics updated: %s" % thisName)

					# ... FOR VERTICAL ARROWS:
					if not thisFont.glyphs[vArrowName]:
						print(u"❌ Reference glyph not found: %s. Cannot update metrics for vertical arrows." % vArrowName)
					else:
						for thisName in self.vArrows:
							if thisName != vArrowName:
								thisGlyph = thisFont.glyphs[thisName]
								if not thisGlyph:
									print(u"⚠️ Warning: '%s' not found in font." % thisName)
								else:
									thisGlyph.leftMetricsKey = "=%s" % vArrowName
									thisGlyph.rightMetricsKey = "=%s" % vArrowName
									self.updateMetricsKeys(thisGlyph)
									print(u"✅ Metrics updated: %s" % thisName)

				if warnAboutLayers:
					Message(
						title="Warning",
						message="The script only corrected the master layers. Double check for brace or bracket layers. These glyphs have non-master layers: %s" %
						", ".join(warnAboutLayers),
						OKButton=None
					)

			self.SavePreferences()

			Glyphs.showMacroWindow()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Fix Arrow Positioning Error: %s" % e)
			import traceback
			print(traceback.format_exc())


FixArrowPositioning()
