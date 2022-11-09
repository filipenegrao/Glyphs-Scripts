#MenuTitle: New Tab with Glyphs of Same Kerning Groups
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new tab containing all members of the left and right kerning groups of the current glyph.
"""

thisFont = Glyphs.font # frontmost font
thisGlyph = Font.selectedLayers[0].parent

if thisGlyph:
	leftGroup = thisGlyph.leftKerningGroup
	rightGroup = thisGlyph.rightKerningGroup

	leftGroupText = "left:\n"
	rightGroupText = "right:\n"

	for g in thisFont.glyphs:
		if g.leftKerningGroup == leftGroup:
			leftGroupText += "/%s" % g.name
		if g.rightKerningGroup == rightGroup:
			rightGroupText += "/%s" % g.name

	Font.newTab("%s %s\n\n%s %s" % (thisGlyph.name, leftGroupText, thisGlyph.name, rightGroupText))
else:
	Message(title="Script Error", message="No glyph currently selected.", OKButton=None)
