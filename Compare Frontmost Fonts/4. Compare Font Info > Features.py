# MenuTitle: Compare Font Info > Features
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Compares the OT features set of the two frontmost fonts and outputs a report in the Macro Window.
"""

from compare import compareLists, lineReport
from GlyphsApp import Glyphs


def removeComments(featureCode):
	lines = featureCode.splitlines()
	for i, line in enumerate(lines):
		if "#" in line:
			lines[i] = line[:line.find("#")]
	featureCode = "\n".join(lines)
	return featureCode


thisFont = Glyphs.fonts[0]  # frontmost font
otherFont = Glyphs.fonts[1]  # second font
thisFileName = thisFont.filepath.lastPathComponent()
otherFileName = otherFont.filepath.lastPathComponent()

# compare prefix, class and feature structure

# collect names:
thisPrefixSet = [p.name for p in thisFont.featurePrefixes if p.active]
thisClassSet = [c.name for c in thisFont.classes if c.active]
thisFeatureSet = [f.name for f in thisFont.features if f.active]
otherPrefixSet = [p.name for p in otherFont.featurePrefixes if p.active]
otherClassSet = [c.name for c in otherFont.classes if c.active]
otherFeatureSet = [f.name for f in otherFont.features if f.active]

compareSet = {
	"Classes": (thisClassSet, otherClassSet),
	"Prefixes": (thisPrefixSet, otherPrefixSet),
	"Features": (thisFeatureSet, otherFeatureSet),
}

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print("Comparing Feature Sets for:".upper())
print()
print("1. %s (family: %s)" % (thisFileName, thisFont.familyName))
print("   ~/%s" % thisFont.filepath.relativePathFromBaseDirPath_("~"))
print("2. %s (family: %s)" % (otherFileName, otherFont.familyName))
print("   ~/%s" % otherFont.filepath.relativePathFromBaseDirPath_("~"))
print()

for compareGroup in ("Prefixes", "Classes", "Features"):
	thisSet, otherSet = compareSet[compareGroup]

	# compare:
	thisSet, otherSet = compareLists(thisSet, otherSet)

	# report in Macro Window
	if thisSet or otherSet:
		if otherSet:
			print(u"❌ %s not in (1) %s\n" % (compareGroup, thisFileName))
			print("  %s" % (", ".join(otherSet)))
		if thisSet:
			print(u"❌ %s not in (2) %s\n" % (compareGroup, otherFileName))
			print("  %s" % (", ".join(thisSet)))
	else:
		print(u"✅ %s: same structure in both fonts." % compareGroup)

print()
print("Detailed Code Comparison:".upper())
print()
for prefix in set([p.name for p in thisFont.featurePrefixes if p.active]):
	# prefixes:
	thisPrefix = "\n".join([f.code for f in thisFont.featurePrefixes if f.name == prefix])  # thisFont.featurePrefixes[prefix]
	otherPrefix = "\n".join([f.code for f in otherFont.featurePrefixes if f.name == prefix])  # otherFont.featurePrefixes[prefix]

	if thisPrefix and otherPrefix:
		# compare:
		thisPrefix, otherPrefix = compareLists(
			removeComments(thisPrefix).splitlines(),
			removeComments(otherPrefix).splitlines(),
			ignoreEmpty=True,
		)
		# report in Macro Window
		lineReport(thisPrefix, otherPrefix, thisFileName, otherFileName, "Prefix %s" % prefix)

for otClass in [c.name for c in thisFont.classes if c.active]:
	# classes:
	thisClass = thisFont.classes[otClass]
	otherClass = otherFont.classes[otClass]

	if thisClass and otherClass:
		# compare code lines:
		thisClassCode, otherClassCode = compareLists(
			removeComments(thisClass.code).split(),
			removeComments(otherClass.code).split(),
			ignoreEmpty=True,
		)
		# report in Macro Window
		lineReport(thisClassCode, otherClassCode, thisFileName, otherFileName, "Class %s" % otClass, commaSeparated=True)

for feature in set([f.name for f in thisFont.features if f.active]):
	thisFeatureCode = "\n".join([f.code for f in thisFont.features if f.name == feature])  # thisFont.features[feature]
	otherFeatureCode = "\n".join([f.code for f in otherFont.features if f.name == feature])  # otherFont.features[feature]

	if thisFeatureCode and otherFeatureCode:
		# compare code lines:
		thisFeatureCode, otherFeatureCode = compareLists(
			removeComments(thisFeatureCode).splitlines(),
			removeComments(otherFeatureCode).splitlines(),
			ignoreEmpty=True,
		)
		# report in Macro Window
		lineReport(thisFeatureCode, otherFeatureCode, thisFileName, otherFileName, "Feature %s" % feature)
