# MenuTitle: Compare Glyphsets
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Compares the glyph set of the two frontmost fonts and outputs a report in the Macro Window.
"""

from GlyphsApp import Glyphs

thisFont = Glyphs.fonts[0]  # frontmost font
otherFont = Glyphs.fonts[1]  # second font

thisFileName = thisFont.filepath.pathComponents()[-1]
otherFileName = otherFont.filepath.pathComponents()[-1]

thisGlyphSet = [g.name for g in thisFont.glyphs if g.export]
otherGlyphSet = [g.name for g in otherFont.glyphs if g.export]

for i in range(len(thisGlyphSet))[::-1]:
	if thisGlyphSet[i] in otherGlyphSet:
		otherGlyphSet.remove(thisGlyphSet.pop(i))

for i in range(len(otherGlyphSet))[::-1]:
	if otherGlyphSet[i] in thisGlyphSet:
		thisGlyphSet.remove(otherGlyphSet.pop(i))

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print("1. %s\n%s\n" % (thisFont.familyName, thisFont.filepath))
print("2. %s\n%s\n" % (otherFont.familyName, otherFont.filepath))
print("Glyphs not in %s:\n" % thisFileName)
print(", ".join(otherGlyphSet))
print()
print("Glyphs not in %s:\n" % otherFileName)
print(", ".join(thisGlyphSet))
print()
