# MenuTitle: Insert Brace Layers for Rotating Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Inserts a number of Brace Layers with continuously scaled and rotated components. Useful for OTVar interpolations with rotating elements.
"""

import vanilla
from GlyphsApp import Glyphs, GSLayer, Message
from mekkablue import mekkaObject


class InsertBraceLayersForComponentRotation(mekkaObject):
	prefDict = {
		"steps": 5,
		"replace": True
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 120
		windowWidthResize = 150  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Layers for Rotating Components",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		self.w.text_1 = vanilla.TextBox((14, 12 + 2, 170, 14), "Insert steps between masters:", sizeStyle='small')
		self.w.steps = vanilla.EditText((185, 11, -15, 20), "5", sizeStyle='small')
		self.w.replace = vanilla.CheckBox((15, 38, -15, 16), "Replace existing Brace Layers", value=True, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Insert", callback=self.InsertBraceLayersForComponentRotationMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def getMasterWeightValue(self, master):
		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			return master.axes[0]
		else:
			# Glyphs 2 code
			return master.weightValue

	def InsertBraceLayersForComponentRotationMain(self, sender):
		try:
			try:
				steps = self.prefInt("steps")
			except Exception as e:  # noqa: F841
				steps = 0
				Message(title="Value Error", message="Cannot find valid number of steps.", OKButton=None)

			replace = True

			if steps > 0:
				thisFont = Glyphs.font  # frontmost font
				masters = thisFont.masters  # all masterss
				numberOfMasters = len(masters)

				if Glyphs.versionNumber >= 3:
					if thisFont.axes:
						axisID = thisFont.axes[0].axisId
				else:
					axisID = True

				if numberOfMasters > 1 and axisID:
					braceLayerValues = {}
					for i in range(1, numberOfMasters):
						prevMaster = masters[i - 1]
						prevValue = self.getMasterWeightValue(prevMaster)
						currMaster = masters[i]
						currValue = self.getMasterWeightValue(currMaster)
						for j in range(steps):
							stepWidth = (currValue - prevValue) / (steps + 1)
							newValue = prevValue + stepWidth * (j + 1)
							braceLayerValues[newValue] = (prevMaster.id, currMaster.id)  # record interpolation masters with brace layer value

					for thisGlyph in [layer.parent for layer in thisFont.selectedLayers]:  # loop through glyphs
						if thisGlyph.mastersCompatible:
							if replace:
								for i in range(len(thisGlyph.layers))[::-1]:
									layerName = thisGlyph.layers[i].name
									if layerName.find("{") < layerName.find("}") and "{" in layerName:
										del thisGlyph.layers[i]

							for thisValue in sorted(braceLayerValues.keys()):
								newLayer = GSLayer()
								newLayer.name = "{%i}" % int(thisValue)
								if Glyphs.versionNumber >= 3:
									newLayer.attributes['coordinates'] = {
										axisID: thisValue
									}
								thisGlyph.layers.append(newLayer)
								newLayer.reinterpolate()
								"""  # is this broken?
								masterLayer1 = thisGlyph.layers[braceLayerValues[thisValue][0]]
								masterLayer2 = thisGlyph.layers[braceLayerValues[thisValue][1]]
								masterValue1 = self.getMasterWeightValue(masterLayer1.associatedFontMaster())
								masterValue2 = self.getMasterWeightValue(masterLayer2.associatedFontMaster())

								for i, thisComponent in enumerate(newLayer.components):
									comp1 = masterLayer1.components[i]
									comp2 = masterLayer2.components[i]
									factor = (thisValue-masterValue1) / float(masterValue2-masterValue1)
									thisComponent.scale = (
										comp1.scale[0] + factor * (comp2.scale[0]-comp1.scale[0]),
										comp1.scale[1] + factor * (comp2.scale[1]-comp1.scale[1]),
										#-1 if thisComponent.scale[0] < 0 else 1,
										#-1 if thisComponent.scale[1] < 0 else 1,
								)
								"""
						else:
							print("%s: not compatible. Left unchanged." % thisGlyph.name)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Insert Brace Layers for Component Rotation Error: %s" % e)
			import traceback
			print(traceback.format_exc())


InsertBraceLayersForComponentRotation()
