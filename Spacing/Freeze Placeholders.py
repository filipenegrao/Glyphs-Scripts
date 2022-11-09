#MenuTitle: Freeze Placeholders
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Turn placeholders in current tab into current glyphs.
"""

try:
	thisFont = Glyphs.font # frontmost font
	currentTab = thisFont.currentTab # current edit tab, if any
	selectedGlyph = thisFont.selectedLayers[0].parent # active layers of selected glyphs

	if currentTab:
		currentTab.text = currentTab.text.replace("/Placeholder", "/%s" % selectedGlyph.name)
	else:
		Message(title="Cannot Freeze Placeholders", message="You must have an edit tab open, and a glyph selected. Otherwise, the script cannot work.", OKButton="Got it")
except Exception as e:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	import traceback
	print(traceback.format_exc())
	Message(
		title="Freezing Placeholders Failed",
		message="An error occurred during the execution of the script. Is a font open, a glyph selected? Check the Macro Window for a detailed error message.",
		OKButton=None
		)
