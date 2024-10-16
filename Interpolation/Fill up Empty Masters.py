# MenuTitle: Fill Up Empty Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Looks for empty master layers and adds shapes of a preferred master.
"""

import vanilla
from copy import copy as copy
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject
from Cocoa import NSImage

labelColors = (
	"🔴 Red",
	"🟠 Orange",
	"🟤 Brown",
	"🟡 Yellow",
	"💚 Light Green",
	"🟢 Dark Green",
	"🩵 Cyan",
	"🔵 Blue",
	"🟣 Purple",
	"🩷 Pink",
	"🩶 Light Gray",
	"🌑 Dark Gray",
)


class FillUpEmptyMasters(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"masterChoice": 0,
		"firstOneWithShapes": 1,
		"addMissingAnchors": 1,
		"copySidebearings": 0,
		"markWithColor": 0,
		"layerColor": 0,
		"overwriteExisting": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 205
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Fill Up Empty Masters",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 16, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Populate empty layers of selected glyphs:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.masterChoiceText = vanilla.TextBox((inset, linePos + 2, 95, 14), "Use shapes from", sizeStyle="small", selectable=True)
		self.w.masterChoice = vanilla.PopUpButton((inset + 95, linePos, -inset - 25, 17), (), sizeStyle="small", callback=self.SavePreferences)
		self.w.masterChoiceUpdate = vanilla.Button((-inset - 18, linePos - 2, -inset - 1, 17), "", callback=self.masterChoiceUpdateAction)
		self.w.masterChoiceUpdate.getNSButton().setImage_(NSImage.imageNamed_("NSRefreshTemplate"))
		self.w.masterChoiceUpdate.getNSButton().setBordered_(False)

		linePos += lineHeight

		self.w.firstOneWithShapes = vanilla.CheckBox((inset, linePos, -inset, 20), "If empty, use first master with shapes", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.addMissingAnchors = vanilla.CheckBox((inset, linePos, -inset, 20), "Add missing default anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.copySidebearings = vanilla.CheckBox((inset, linePos, -inset, 20), "Also copy sidebearings", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.markWithColor = vanilla.CheckBox((inset, linePos, 165, 20), "Color-mark filled-up layers:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.layerColor = vanilla.PopUpButton((inset + 165, linePos + 1, 105, 17), labelColors, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.overwriteExisting = vanilla.CheckBox((inset, linePos, 165, 20), "Overwrite Existing Outlines❗️", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Status:
		self.w.status = vanilla.TextBox((inset - 5, linePos + 7, -75 - inset, 15), "", sizeStyle="small", selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Fill Up", callback=self.FillUpEmptyMastersMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def masterChoiceUpdateAction(self, sender):
		self.updateUI()

	def updateUI(self, sender=None):
		self.w.layerColor.enable(self.pref("markWithColor"))
		if Glyphs.font:
			masterNames = [m.name for m in Glyphs.font.masters]
			self.w.masterChoice.setItems(masterNames)
			if len(masterNames) < self.w.masterChoice.get() + 1:
				self.w.masterChoice.set(len(masterNames) - 1)
			else:
				self.w.masterChoice.set(self.pref("masterChoice"))
			self.w.runButton.enable(1)
		else:
			self.w.masterChoice.setItems([])
			self.w.runButton.enable(0)

	def FillUpEmptyMastersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Fill Up Empty Masters Report for {reportName}")
				print()
				sourceMaster = thisFont.masters[self.pref("masterChoice")]
				sourceID = sourceMaster.id
				selectedGlyphs = set([layer.parent for layer in thisFont.selectedLayers])
				layerCount = 0
				for thisGlyph in selectedGlyphs:
					self.w.status.set(f"🔤 Filling up {thisGlyph.name}...")
					sourceLayer = thisGlyph.layers[sourceID]
					if not sourceLayer.shapes and self.pref("firstOneWithShapes"):
						sourceLayer = None
						for master in thisFont.masters:
							if thisGlyph.layers[master.id].shapes:
								sourceLayer = thisGlyph.layers[master.id]
								print(f"🔤 Filling up {thisGlyph.name} from layer {master.name}")
								break

					if not sourceLayer:
						print(f"⚠️ No shapes for filling up in: {thisGlyph.name}")
						self.w.status.set(f"⚠️ No shapes: {thisGlyph.name}")
						continue

					for targetLayer in thisGlyph.layers:
						if (targetLayer.isMasterLayer or targetLayer.isSpecialLayer) and targetLayer != sourceLayer and (not targetLayer.shapes or self.pref("overwriteExisting")):
							targetLayer.clear()
							layerCount += 1
							for sourceShape in sourceLayer.shapes:
								targetLayer.shapes.append(copy(sourceShape))
							for sourceAnchor in sourceLayer.anchors:
								targetLayer.anchors.append(copy(sourceAnchor))

							if self.pref("copySidebearings"):
								targetLayer.LSB = sourceLayer.LSB
								targetLayer.RSB = sourceLayer.RSB

							if self.pref("addMissingAnchors"):
								targetLayer.addMissingAnchors()

							if self.pref("markWithColor"):
								targetLayer.color = self.pref("layerColor")

			finalMessage = f"✅ Done. Filled up {layerCount} layer{'' if layerCount == 1 else 's'} in {len(selectedGlyphs)} glyph{'' if len(selectedGlyphs) == 1 else 's'}."
			print(f"\n{finalMessage}")
			self.w.status.set(finalMessage)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Fill Up Empty Masters Error: {e}")
			import traceback
			print(traceback.format_exc())


FillUpEmptyMasters()
