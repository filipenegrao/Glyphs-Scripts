# MenuTitle: Feature Code Tweaks
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Adds tweaks to OT feature code. Reports in Macro window.
"""

import vanilla
from GlyphsApp import Glyphs, GSFeature, GSClass, GSFeaturePrefix
from mekkaCore import mekkaObject


def filterActiveCode(code):
	activeCode = ""
	for line in code.splitlines():
		line = line.strip()
		if line and line[0] != "#" and not line.startswith("lookup") and not line.startswith("}") and not line.startswith("feature"):
			if "#" in line:
				activeCode += line[:line.find("#")]
			else:
				activeCode += line
			activeCode += "\n"
	return activeCode


def correspondingUppercaseForGlyphName(glyphname):
	glyphinfo = Glyphs.glyphInfoForName(glyphname)
	if not glyphinfo:
		return None
	else:
		lowercaseChar = glyphinfo.unicharString()
		if not lowercaseChar:
			return None
		else:
			uppercaseChar = glyphinfo.unicharString().upper()
			uppercaseName = Glyphs.niceGlyphName(uppercaseChar)
			if not uppercaseName:
				return None
			else:
				return uppercaseName


def addClass(otClassName, thisFont, forceUpdate=False):
	autoFeatures = ("All", "AllLetters", "Uppercase", "Lowercase")

	# Add class:
	otClass = thisFont.classes[otClassName]
	if not otClass:
		otClass = GSClass()
		otClass.name = otClassName
		if otClassName in autoFeatures:
			otClass.automatic = True
		thisFont.classes.append(otClass)
		print(u"✅ OT class @%s added." % otClassName)

	# Force the update if required:
	if forceUpdate and not otClass.automatic:
		otClass.automatic = True
		print(u"✅ OT class @%s: Automated code." % otClassName)

		# TODO: check if class still exists after force update, run again without forceUpdate

	# Update class:
	if otClass.automatic:
		otClass.update()
		print(u"✅ OT class @%s: Updated automatic code." % otClassName)
	else:
		print(u"⚠️ Warning: OT class @%s is not set to automatic." % otClassName)


def updateAndAutodisableFeatureInFont(featureName, thisFont):
	feature = thisFont.features[featureName]
	if feature:
		if feature.automatic:
			# update code, report if something changed
			oldCode = feature.code
			feature.update()
			if feature.code != oldCode:
				print(u"✅ Updated %s feature code." % featureName)
			# disable automation and report:
			feature.automatic = False
			print(u"✅ Disabled automation in %s." % featureName)
	else:
		print(u"⚠️ Feature %s does not exist (yet)." % featureName)


def createManyToOneFromDict(codeDict, thisFont):
	featureLines = ""
	ligNames = sorted(codeDict.keys(), key=lambda thisListItem: thisListItem.lower())

	for ligName in ligNames:

		# check if ligature glyphs is in font:
		ligGlyph = thisFont.glyphs[ligName]
		if ligGlyph and ligGlyph.export:

			# check if all parts are present:
			allParts = codeDict[ligName]
			allPartsPresent = True
			for thisPart in allParts:
				partGlyph = thisFont.glyphs[ligName]
				if not (partGlyph and partGlyph.export):
					allPartsPresent = False

			if allPartsPresent:

				# build code line:
				separateGlyphs = " ".join(allParts)
				featureLines += "	sub %s by %s;\n" % (separateGlyphs, ligName)

				# frequent autocorrect replacements:
				autocorrectDict = {
					"hyphen hyphen": ("endash", "emdash"),
					"period period period": ("ellipsis"),
				}
				for autocorrectString in autocorrectDict:
					possibleReplacements = autocorrectDict[autocorrectString]
					if autocorrectString in separateGlyphs:
						replacementClass = []
						for replacement in possibleReplacements:
							if thisFont.glyphs[replacement]:
								replacementClass.append(replacement)
						if replacementClass:
							replacementCode = " ".join(replacementClass)
							if len(replacementClass) > 1:
								replacementCode = "[%s]" % replacementCode
							separateGlyphs = separateGlyphs.replace(autocorrectString, replacementCode)
							featureLines += "	sub %s by %s;\n" % (separateGlyphs, ligName)

				print(u"✅ Adding ligature substitution for %s." % (ligName))
			else:
				print(u"⚠️ Warning: not all parts present for %s (%s), no substitution added." % (ligName, ", ".join(allParts)))
		else:
			print(u"⚠️ Warning: %s is not present (or not set to export), no substitution added." % ligName)
	return featureLines


def wrapCodeInLookup(featureCode, lookupName):
	code = "lookup %s {\n%s\n} %s;\n" % (lookupName, featureCode.rstrip(), lookupName)
	return code


def updatedCode(oldCode, beginSig, endSig, newCode):
	"""Replaces text in oldCode with newCode, but only between beginSig and endSig."""
	beginOffset = oldCode.find(beginSig)
	endOffset = oldCode.find(endSig) + len(endSig)
	newCode = oldCode[:beginOffset] + beginSig + newCode + "\n" + endSig + oldCode[endOffset:]
	return newCode


def createOTFeature(
	featureName="calt",
	featureCode="# empty feature code",
	targetFont=Glyphs.font,
	codeSig="CUSTOM-CONTEXTUAL-ALTERNATES",
	appendCode=True,
	addNote=False,
):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	featureName: name of the feature (str),
	featureCode: the AFDKO feature code (str),
	targetFont: the GSFont object receiving the feature,
	codeSig: the code signature (str) used as delimiters.
	"""

	beginSig = "# BEGIN " + codeSig + "\n"
	endSig = "# END " + codeSig + "\n"
	featureCode = featureCode.rstrip()

	if featureName in [f.name for f in targetFont.features]:
		# feature already exists:
		targetFeature = targetFont.features[featureName]

		if beginSig in targetFeature.code:
			# replace old code with new code:
			targetFeature.code = updatedCode(targetFeature.code, beginSig, endSig, featureCode)
		else:
			if appendCode:
				# append new code:
				targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig
			else:
				# prepend new code:
				targetFeature.code = beginSig + featureCode + "\n" + endSig + "\n" + targetFeature.code

		print(u"✅ Updated existing OT feature '%s'." % featureName)
	else:
		# create feature with new code:
		targetFeature = GSFeature()
		targetFeature.name = featureName
		targetFeature.code = beginSig + featureCode + "\n" + endSig
		targetFont.features.append(targetFeature)
		print(u"✅ Created new OT feature '%s'." % featureName)

	if addNote:
		if not targetFeature.notes:
			targetFeature.notes = ""

		if featureCode not in targetFeature.notes:
			position = "end" if appendCode else "beginning"
			manualInstruction = "# Add at %s:\n%s\n\n" % (position, featureCode)
			targetFeature.notes = manualInstruction + targetFeature.notes
			print(u"✅ Added manual instructions into notes of OT feature '%s'." % featureName)


def featureLineContainingXAlsoContains(font, featureName="ccmp", lineContaining="@Markscomb =", alsoContains="acute"):
	"""
	Does feature featureName:
	a. have a line containing lineContaining?
	b. and if so, does that line contain alsoContains?
	"""
	feature = font.features[featureName]
	if feature:
		featureLines = feature.code.splitlines()
		relevantFeatureLines = [line for line in featureLines if lineContaining in line]
		for line in relevantFeatureLines:
			if alsoContains in line:
				return True
	return False


class FeatureCodeTweaks(mekkaObject):
	prefDict = {
		"scFeatureFix": 0,
		"addArrowLigs": 0,
		"germanLocalization": 0,
		"dutchLocalization": 0,
		"decomposePresentationForms": 0,
		"includeIJ": 0,
		"includeLdot": 0,
		"includeBalkan": 0,
		"repeatDecompositionInSC": 0,
		"repeatDecompositionInOtherAffectedFeatures": 0,
		"disableLiga": 0,
		"fShortSubstitution": 0,
		"magistra": 0,
		"ssXX2salt": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 370
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Feature Code Tweaks",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset, lineHeight, currentHeight = 15, 20, 10

		self.w.text = vanilla.TextBox((inset - 1, currentHeight + 2, -inset, lineHeight), __doc__[1:], sizeStyle='small')
		currentHeight += lineHeight

		self.w.scFeatureFix = vanilla.CheckBox((inset, currentHeight, -inset, lineHeight), "Fix smallcap features (smcp/c2sc)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.scFeatureFix.getNSButton().setToolTip_("Adds missing smallcap substitutions for glyphs like idotless, jdotless, kgreenlandic and longs.")
		currentHeight += lineHeight

		self.w.addArrowLigs = vanilla.CheckBox((inset, currentHeight, -inset, lineHeight), "Add arrow ligatures (dlig)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.addArrowLigs.getNSButton().setToolTip_("Adds ligatures of hyphens with greater and less for left and right arrows, and double hyphen ligatures for arrows with .long suffix.")
		currentHeight += lineHeight

		self.w.germanLocalization = vanilla.CheckBox((inset, currentHeight, -inset, lineHeight), "Add German cap sharp S code (locl, calt)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.germanLocalization.getNSButton().setToolTip_("Automatically substitutes lowercase sharp s for uppercase sharp S between other uppercase letters. Adds a lookup in locl and calls the lookup in calt.")
		currentHeight += lineHeight

		self.w.dutchLocalization = vanilla.CheckBox((inset, currentHeight, -inset, lineHeight), "Add proper Dutch localization (locl)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.dutchLocalization.getNSButton().setToolTip_("Adds a different Dutch localization than the default. Will not substitute uppercase /J for /Jacute if a combining accent follows (as would be the case if the user follows the proper Unicode text entry).")
		currentHeight += lineHeight

		# DECOMPOSE PRESENTATION FORMS:

		self.w.decomposePresentationForms = vanilla.CheckBox((inset, currentHeight, -inset, lineHeight), "Decompose Latin presentation forms like fi and fl (ccmp)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.decomposePresentationForms.getNSButton().setToolTip_("Adds precomposed but ligature characters like /fi and /fl (which are not supposed to be used in texts) to ccmp, and decomposes them into their character equivalents, f+i, f+l, etc. Strongly recommended because it preserves tracking and smallcap compatibility.")
		currentHeight += lineHeight

		self.w.includeLdot = vanilla.CheckBox((inset * 3, currentHeight, -inset, lineHeight), "Include Ldot, ldot, napostrophe (if present)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeLdot.getNSButton().setToolTip_("Includes deprecated Ldot/ldot in ccmp decomposition.")
		currentHeight += lineHeight

		self.w.includeBalkan = vanilla.CheckBox((inset * 3, currentHeight, -inset, lineHeight), u"Include Balkan digraphs ǳ, ǆ, ǉ, ǌ (if present)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeBalkan.getNSButton().setToolTip_("Includes deprecated Slavic/Balkan digraphs in ccmp decomposition.")
		currentHeight += lineHeight

		self.w.includeIJ = vanilla.CheckBox((inset * 3, currentHeight, -inset, lineHeight), "Include IJ, ij (if present)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeIJ.getNSButton().setToolTip_("Includes unused Durch and deprecated Afrikaans digraphs in ccmp decomposition.")
		currentHeight += lineHeight

		self.w.disableLiga = vanilla.CheckBox((inset * 3, currentHeight, -inset, lineHeight), u"Disable affected ligature lines in liga, dlig (if present)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.disableLiga.getNSButton().setToolTip_("Also disables ligatures in liga. Only recommended if your fi, fl, etc. look exactly like separate f+i, f+l, etc., i.e., if they are not really ligated.")
		currentHeight += lineHeight

		self.w.repeatDecompositionInSC = vanilla.CheckBox((inset * 3, currentHeight, -inset, lineHeight), u"Repeat decomposition in smcp and c2sc", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.repeatDecompositionInSC.getNSButton().setToolTip_("Calls the ccmp lookup at the beginning of smcp and c2sc. This makes decompositions (and hence, the small caps) work in the Adobe (Latin) Composers, which ignore ccmp.")
		currentHeight += lineHeight

		self.w.repeatDecompositionInOtherAffectedFeatures = vanilla.CheckBox((inset * 3, currentHeight, -inset, lineHeight), u"Repeat decomposition in affected (non-SC) features", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.repeatDecompositionInOtherAffectedFeatures.getNSButton().setToolTip_("Calls the ccmp lookup at the beginnings of all features that substitute affected glyphs, e.g., in ss01. This option ignores smcp and c2sc. ATTENTION: cannot parse nested lookups yet, so the result may be incomplete.")
		currentHeight += lineHeight

		self.w.fShortSubstitution = vanilla.CheckBox((inset, currentHeight, -inset, lineHeight), "Add f.short contextual substitutions (calt)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.fShortSubstitution.getNSButton().setToolTip_("Not implemented yet.")
		currentHeight += lineHeight

		self.w.magistra = vanilla.CheckBox((inset, currentHeight, -inset, lineHeight), "Add Mag.a substitution (calt) and 90% kerning", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.magistra.getNSButton().setToolTip_("Automatic feature code substitution for Austrian academic title Mag.a (Magistra). Recommended for fonts for the Austrian market or an Austrian client.")
		currentHeight += lineHeight

		self.w.ssXX2salt = vanilla.CheckBox((inset, currentHeight, -inset, lineHeight), "Overwrite salt feature with ssXX lookups", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.ssXX2salt.getNSButton().setToolTip_("Creates a universal salt feature including all ssXX substitutions. Careful: does not update, but overwrite the feature code. Will park the old feature code in the feature notes, though.")
		currentHeight += lineHeight

		# self.w.scFeatureFix.enable(False)
		self.w.fShortSubstitution.enable(False)

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Tweak", sizeStyle='regular', callback=self.FeatureCodeTweaksMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print(u"⚠️ Note: 'Feature Code Tweaks' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self):
		onOrOff = self.pref("decomposePresentationForms")
		self.w.includeIJ.enable(onOrOff)
		self.w.includeLdot.enable(onOrOff)
		self.w.includeBalkan.enable(onOrOff)
		self.w.disableLiga.enable(onOrOff)
		self.w.repeatDecompositionInSC.enable(onOrOff)
		self.w.repeatDecompositionInOtherAffectedFeatures.enable(onOrOff)

	def decomposePresentationForms(self, feature="ccmp", includeIJ=False, includeLdot=False):
		decomposeDict = {
			"ff": ("f", "f"),
			"fi": ("f", "i"),
			"ffi": ("f", "f", "i"),
			"fl": ("f", "l"),
			"ffl": ("f", "f", "l"),
			"s_t": ("s", "t"),
			"longs_t": ("longs", "t"),
		}

		if self.pref("includeIJ"):
			includeIJ = {
				"ij": ("i", "j"),
				"IJ": ("I", "J"),
			}
			decomposeDict.update(includeIJ)

		if self.pref("includeLdot"):
			includeLdot = {
				"Ldot": ("L", "periodcentered.loclCAT.case"),
				"ldot": ("l", "periodcentered.loclCAT"),
				"napostrophe": ("quoteright", "n"),
			}
			decomposeDict.update(includeLdot)

		if self.pref("includeBalkan"):
			includeBalkan = {
				"LJ": ("L", "J"),
				"lj": ("l", "j"),
				"Lj": ("L", "j"),
				"NJ": ("N", "J"),
				"Nj": ("N", "j"),
				"nj": ("n", "j"),
				"DZ": ("D", "Z"),
				"Dz": ("D", "z"),
				"dz": ("d", "z"),
				"DZcaron": ("D", "Zcaron"),
				"Dzcaron": ("D", "zcaron"),
				"dzcaron": ("d", "zcaron"),
			}
			decomposeDict.update(includeBalkan)

		# collect feature code for all present glyphs:
		featureLines = ""
		thisFont = Glyphs.font
		ligNames = sorted(decomposeDict.keys(), key=lambda thisListItem: thisListItem.lower())
		disableList = []
		for ligName in ligNames:
			ligGlyph = thisFont.glyphs[ligName]
			if ligGlyph and ligGlyph.export:
				# check if all decomposition parts are in the font:
				decomposeParts = decomposeDict[ligName]
				shouldAddLine = True
				shouldConsiderUCInstead = False
				actualDecomposeParts = [name for name in decomposeParts]
				for i, glyphName in enumerate(decomposeParts):
					glyph = thisFont.glyphs[glyphName]

					# this should give the UC name in an all-cap double-encoding font:
					if glyph:
						actualDecomposeParts[i] = glyph.name

					# it it does not exist, check if a corresponding UC is there (all-cap font):
					if not glyph:
						uppercaseGlyphName = correspondingUppercaseForGlyphName(glyphName)
						if uppercaseGlyphName:
							uppercaseGlyph = thisFont.glyphs[uppercaseGlyphName]
							if uppercaseGlyph:
								shouldConsiderUCInstead = True
								actualDecomposeParts[i] = uppercaseGlyphName

					# if it exists, check if it also exports:
					elif not glyph.export:
						shouldAddLine = False

				if not shouldAddLine:
					print(u"⚠️ Warning: not all parts (%s) for decomposition of %s present and exporting." % (", ".join(decomposeParts), ligName))
				else:
					# build and add the code line:
					if ligGlyph.unicode is not None:
						disableList.append(actualDecomposeParts)
						decomposeResult = " ".join(actualDecomposeParts)
						featureLines += "	sub %s by %s;\n" % (ligName, decomposeResult)
						print(u"✅ %s: Adding decomposition for %s." % (feature, ligName))
					else:
						print(u"⚠️ Ligature %s has no Unicode, so no decomposition added." % ligName)

		# check if any code has been collected:
		if not featureLines:
			print(u"⚠️ Warning: No (exporting) presentation-form ligatures found in font, %s unchanged." % feature)
		else:
			lookupName = "latinPresentationForms"

			# wrap featureLines in lookup block
			featureLines = wrapCodeInLookup(featureLines, lookupName)

			# see if ccmp exists, and create it if not:
			ccmpFeature = thisFont.features[feature]
			if not ccmpFeature:
				ccmpFeature = GSFeature()
				ccmpFeature.name = feature
				ccmpFeature.code = "# Warning: %s created by script, please review." % feature
				ccmpFeature.automatic = False
				print(u"⚠️ Warning: added empty, non-automated %s feature. Please review." % feature)

				# check if aalt exists in first place:
				aaltExists = False
				if thisFont.features:
					if thisFont.features[0].name == "aalt":
						aaltExists = True
				thisFont.features.insert(
					1 if aaltExists else 0,
					ccmpFeature,
				)

			# prepare feature and inject code:
			updateAndAutodisableFeatureInFont(feature, thisFont)
			createOTFeature(
				featureName=ccmpFeature.name,
				featureCode=featureLines,
				targetFont=thisFont,
				codeSig="Decompose presentation forms",
				appendCode=False,
				addNote=True,
			)

			# repeat in Small Caps if necessary:

			affectedFeatures = []
			if self.pref("repeatDecompositionInSC"):
				affectedFeatures.extend(("smcp", "c2sc"))
			if self.pref("repeatDecompositionInOtherAffectedFeatures"):
				for affectedFeature in thisFont.features:
					if affectedFeature.name != feature:  # ccmp
						print("-----", affectedFeature.name)
						shouldAdd = False
						activeCode = filterActiveCode(affectedFeature.code)
						for removeWord in (";", "sub", "by", "pos", "feature"):
							activeCode = activeCode.replace(removeWord, "")
						activeCodeWords = activeCode.split()
						for ligName in decomposeDict:
							for particle in decomposeDict[ligName]:
								if particle in activeCodeWords:
									shouldAdd = True
						if shouldAdd:
							affectedFeatures.append(affectedFeature.name)

			if affectedFeatures:
				lookupCall = "lookup %s;" % lookupName
				for featureTag in affectedFeatures:
					affectedFeature = thisFont.features[featureTag]
					if not feature:
						print(u"🤷🏻‍♀️ No %s feature found, could not repeat decomposition lookup." % featureTag)
					else:
						createOTFeature(
							featureName=featureTag,
							featureCode=lookupCall,
							targetFont=thisFont,
							codeSig="Decompose presentation forms",
							appendCode=False,
							addNote=True,
						)
						if affectedFeature.automatic:
							affectedFeature.automatic = False
							print(u"✅ Disabled automatism for '%s'." % featureTag)

						print(u"✅ Added call for decomposition lookup in %s." % featureTag)

			# disable codelines if necessary:

			if self.pref("disableLiga"):
				# collect code to recognize (for disabling further below)
				linestarts = []
				for ligParts in disableList:
					linestart = "sub %s by" % " ".join(ligParts)
					linestarts.append(linestart)

				# look for code snippets and disable where found:
				for ligatureFeatureTag in ("dlig", "liga"):
					feature = thisFont.features[ligatureFeatureTag]
					if feature:
						originalCode = feature.code
						codeLines = originalCode.splitlines()
						for i, codeLine in enumerate(codeLines):
							for linestart in linestarts:
								if codeLine.startswith(linestart):
									codeLines[i] = "# %s" % codeLine
									if feature.automatic:
										feature.automatic = False
										print(u"✅ Disabled automatism for '%s'." % ligatureFeatureTag)
									print(u"✅ Commented out line in %s: %s" % (ligatureFeatureTag, codeLine))

						newCode = "\n".join(codeLines)
						if originalCode == newCode or feature.automatic:
							print(u"🤷🏻‍♀️ Feature %s not changed. No ligatures to disable." % ligatureFeatureTag)
						else:
							thisFont.features[ligatureFeatureTag].code = newCode
							print(u"✅ %s: updated feature code." % ligatureFeatureTag)

	def dutchLocalization(self, feature="locl"):
		"""
		lookup NLD {
			language NLD;
			sub iacute j' by jacute;
			# Try other ignore line if first one does not work:
			ignore sub J' [@MarkscombCase @Markscomb];
			# ignore sub J' @CombiningTopAccents;
			sub Iacute J' by Jacute;
			# Make sure Glyph Info for ...comb.sc accents has subcategory=Nonspacing
			# Don't forget: j.sc=jdotless.sc (& verify kerning groups)
		} NLD;
		# DO NOT FORGET TO UPDATE LANGUAGESYSTEMS
		# DO NOT FORGET TO REMOVE DEFAULT NLD CODE
		"""
		thisFont = Glyphs.font

		# check for I, J, Iacute, Jacute, i, j, iacute, jacute, jdotless:

		# collect exporting combining top accents:
		ccmpFeature = thisFont.features["ccmp"]
		markCode = None
		if ccmpFeature and "@Markscomb" in ccmpFeature.code and featureLineContainingXAlsoContains(
			thisFont, featureName="ccmp", lineContaining="@Markscomb =", alsoContains="acute"
		):
			# reuse ccmp classes:
			wordsInFeature = ccmpFeature.code.split()
			marks = []
			for searchWord in ("@Markscomb", "@MarkscombCase"):
				if searchWord in wordsInFeature:
					marks.append(searchWord)
			markCode = " ".join(marks)
			if len(marks) > 1:
				markCode = "[%s]" % markCode
		elif ccmpFeature and "@CombiningTopAccents" in ccmpFeature.code and featureLineContainingXAlsoContains(
			thisFont, featureName="ccmp", lineContaining="@CombiningTopAccents =", alsoContains="acute"
		):
			# reuse ccmp class:
			markCode = "@CombiningTopAccents"
		else:
			# build own class:
			accentNames = [g.name for g in thisFont.glyphs if g.category == "Mark" and g.subCategory == "Nonspacing"]
			if not accentNames:
				print(u"⚠️ Warning: No combining accents found in font. Consider adding at least acutecomb(.case/.sc).")
			else:
				markCode = " ".join(accentNames)
				if len(accentNames) > 1:
					markCode = "[%s]" % markCode

		if not markCode:
			ignoreLine = ""
		else:
			ignoreLine = "\tignore sub J' %s;\n" % markCode

		loclCode = "\tlanguage NLD;"
		originalLength = len(loclCode)
		codesNLD = (
			("\n\tsub iacute j' by jacute;", ("jacute", "j", "iacute")),
			("\n%s\tsub Iacute J' by Jacute;" % ignoreLine, ("Iacute", "J", "Jacute")),
		)

		for codeLineData in codesNLD:
			lineToAdd = codeLineData[0]
			partsForCode = codeLineData[1]
			addLine = True
			for glyphName in partsForCode:
				glyph = thisFont.glyphs[glyphName]
				if not glyph or not glyph.export:
					addLine = False
					print(u"⚠️ Warning: Necessary glyph %s is missing or not exporting. Feature code will be incomplete." % glyphName)
			if addLine:
				loclCode += lineToAdd

		if not len(loclCode) > originalLength:
			print(u"⛔️ Error: Could not add any NLD code, %s unchanged." % feature)
		else:
			# prepare locl code:
			loclCode = wrapCodeInLookup(loclCode, "NLD")

			# prepare OT feature:
			updateAndAutodisableFeatureInFont("locl", thisFont)
			loclFeature = thisFont.features["locl"]

			if not loclFeature:
				print(u"⛔️ Error: Feature locl not present anymore. Aborting.")
			else:

				# Remove existing NLD code:
				if "NLD" in loclFeature.code:
					codeLines = loclFeature.code.splitlines()
					updatedCode = ""
					isDutch = False
					for line in codeLines:
						if line.startswith("language NLD;"):
							isDutch = True
						elif line.startswith("language "):
							isDutch = False
						if not isDutch or line.startswith("#"):
							updatedCode += line
							updatedCode += "\n"
					if loclFeature.code != updatedCode:
						loclFeature.code = updatedCode
						print(u"✅ Removed old NLD code from locl.")

				# Add/update NLD code:
				createOTFeature(
					featureName="locl",
					featureCode=loclCode,
					targetFont=thisFont,
					codeSig="Dutch accented IJ/ij",
					appendCode=True,
					addNote=True,
				)

			# TODO create jdotless.sc

	def germanLocalization(self, feature="calt"):
		thisFont = Glyphs.font
		ucClassName = "Uppercase"

		lcSharpS = thisFont.glyphs["germandbls"]
		ucSharpS = thisFont.glyphs["germandbls.calt"]
		if not ucSharpS or not ucSharpS.export:
			ucSharpS = thisFont.glyphs["Germandbls"]

		if not lcSharpS or not ucSharpS:
			print(u"⚠️ Warning: No LC and UC sharp s found in the font, %s unchanged." % feature)
		elif not lcSharpS.export or not ucSharpS.export:
			print(u"⚠️ Warning: /%s and /%s are not both set to export, %s unchanged." % (
				lcSharpS.name,
				ucSharpS.name,
				feature,
			))
		else:
			# Add @Uppercase:
			addClass("Uppercase", thisFont)

			# Feature code:
			lookupName = "uppercaseSharpS"
			featureLines = "\tsub @%s @%s %s' by %s;\n\tsub %s' @%s by %s;" % (
				ucClassName,
				ucClassName,
				lcSharpS.name,
				ucSharpS.name,
				# ucClassName,
				lcSharpS.name,
				ucClassName,
				ucSharpS.name,
			)
			featureLines = wrapCodeInLookup(featureLines, lookupName)

			# see if locl exists, and create it if not:
			loclFeature = thisFont.features["locl"]
			if not loclFeature:
				loclFeature = GSFeature()
				loclFeature.name = "locl"
				loclFeature.code = "# Warning: locl created by script, please review."
				loclFeature.automatic = False

				# check if aalt/ccmp exist at beginning place:
				insertIndex = 0
				if thisFont.features:
					for featureIndex in (0, 1):
						thisFeature = thisFont.features[featureIndex]
						if thisFeature:
							if thisFeature.name in ("aalt", "ccmp"):
								insertIndex += 1
				thisFont.features.insert(insertIndex, loclFeature)
				print(u"✅ Added locl feature at index %i." % insertIndex)

			# if locl is automated, update it once more and disable automation:
			updateAndAutodisableFeatureInFont("locl", thisFont)

			# add lookup to locl:
			loclCode = "language DEU;\n%s\n" % featureLines
			createOTFeature(
				featureName="locl",
				featureCode=loclCode,
				targetFont=thisFont,
				codeSig="German cap sharp s",
				appendCode=True,
				addNote=True,
			)

			# call lookup in calt:
			caltCode = "lookup %s;" % lookupName
			createOTFeature(
				featureName=feature,
				featureCode=caltCode,
				targetFont=thisFont,
				codeSig="German cap sharp s",
				appendCode=True,
				addNote=True,
			)

			# Update Languagesystems:
			prefixName = "Languagesystems"
			prefix = thisFont.featurePrefixes[prefixName]
			if not prefix:
				prefix = GSFeaturePrefix()
				prefix.name = prefixName
				prefix.automatic = True
				thisFont.featurePrefixes.insert(prefix, 0)
				print(u"✅ Added 'Languagesystems' to feature code prefixes.")

			if not prefix.automatic:
				prefix.automatic = True
				print(u"✅ Automated 'Languagesystems' prefix.")

			oldCode = prefix.code
			prefix.update()
			if prefix.code != oldCode:
				print(u"✅ Updated 'Languagesystems' prefix.")

	def addArrowLigs(self, feature="dlig"):
		"""
		sub hyphen hyphen greater by rightArrow.long;
		sub hyphen greater by rightArrow;
		sub less hyphen hyphen by leftArrow.long;
		sub less hyphen by leftArrow;
		sub less hyphen greater by leftRightArrow;
		sub less hyphen hyphen greater by leftRightArrow.long;
		"""
		thisFont = Glyphs.font
		ligDict = {
			"leftArrow": ["less", "hyphen"],
			"leftArrow.long": ["less", "hyphen", "hyphen"],
			"leftRightArrow": ["less", "hyphen", "greater"],
			"leftRightArrow.long": ["less", "hyphen", "hyphen", "greater"],
			"rightArrow": ["hyphen", "greater"],
			"rightArrow.long": ["hyphen", "hyphen", "greater"],
		}

		# create feature code:
		featureLines = createManyToOneFromDict(ligDict, thisFont)
		if not featureLines:
			print(u"🤷🏻‍♀️ Warning: could not create arrow ligatures, %s unchanged." % feature)
		else:
			# wrap featureLines in lookup block:
			featureLines = wrapCodeInLookup(featureLines, "arrows")

			# add to dlig:
			createOTFeature(
				featureName=feature,
				featureCode=featureLines,
				targetFont=thisFont,
				codeSig="Arrows as ligatures",
				appendCode=True,
				addNote=True,
			)

	def magistraSubstitution(self, feature="calt"):
		"""
		sub M a g period a' by ordfeminine;
		# add .sc
		pos M a g period a' <-50 0 -50 0>;
		"""
		thisFont = Glyphs.font

		canBuildCode = True
		requiredGlyphs = ("M", "a", "g", "period", "ordfeminine")
		for glyphName in requiredGlyphs:
			glyph = thisFont.glyphs[glyphName]
			if not glyph:
				print(u"⛔️ Missing glyph '%s' required for the feature code." % glyphName)
				canBuildCode = False
			elif not glyph.export:
				print(u"⛔️ Glyph '%s' required for feature code exists, but is not exporting." % glyphName)
				canBuildCode = False

		if not canBuildCode:
			print(u"⚠️ Leaving %s unchanged." % feature)
		else:
			# add class if missing:
			addClass("AllLetters", thisFont, forceUpdate=True)

			# add feature code
			featureCode = "\tignore sub M a g period a' @AllLetters;"
			featureCode += "\n\tsub M a g period a' by ordfeminine;"
			featureCode = wrapCodeInLookup(featureCode, "magistra")
			createOTFeature(
				featureName=feature,
				featureCode=featureCode,
				targetFont=thisFont,
				codeSig="Magistra",
				appendCode=True,
				addNote=True,
			)

			# add kerning:
			for thisMaster in thisFont.masters:
				masterID = thisMaster.id

				# take the smaller glyph width and kern by 90% of that:
				minimalWidth = min(thisFont.glyphs["period"].layers[masterID].width, thisFont.glyphs["ordfeminine"].layers[masterID].width)

				# compoensate by kerning value on Other side: Mag<>.
				g = thisFont.glyphs["g"]
				period = thisFont.glyphs["period"]
				kernValueOnOtherSide = 0
				potentialKernValuesOnOtherSide = (
					thisFont.kerningForPair(masterID, "@MMK_L_%s" % g.rightKerningGroup, "@MMK_R_%s" % period.leftKerningGroup),
					thisFont.kerningForPair(masterID, "g", "@MMK_R_%s" % period.leftKerningGroup),
					thisFont.kerningForPair(masterID, "@MMK_L_%s" % g.rightKerningGroup, "period"),
					thisFont.kerningForPair(masterID, "g", "period"),
				)
				for value in potentialKernValuesOnOtherSide:
					if value < 100000:
						kernValueOnOtherSide = value

				# calculate and add kerning:
				kernValue = round(-0.9 * minimalWidth - kernValueOnOtherSide)
				if abs(kernValue) > 5.0:
					thisFont.setKerningForPair(masterID, "period", "ordfeminine", kernValue)
					print(u"✅ Added kerning for period-ordfeminine (%.1f) in master '%s'" % (kernValue, thisMaster.name))
				else:
					print(u"⚠️ Calculated kerning for period-ordfeminine too small (%.1f), no pair added in master '%s'" % (kernValue, thisMaster.name))

	def fShortSubstitution(self, feature="calt"):
		"""
		@TooHighOnLeftSide = [b eth h hbar i iacute ibreve icaron icircumflex idieresis idotaccent idotbelow igrave imacron iogonek itilde j k kcommaaccent l lacute lcaron lcommaaccent ldot ncaron ntilde obreve ocaron ocircumflex odieresis ograve omacron otilde thorn rcaron scaron germandbls ubreve ucaron ucircumflex udieresiscaron udieresisgrave udieresismacron ugrave uhungarumlaut umacron utilde ygrave zcaron parenright braceright bracketright parenright.case braceright.case bracketright.case quotedblright quoteright quotedblleft quoteleft quotedbl quotesingle];
		sub f' @TooHighOnLeftSide by f.short;
		# other short variants?
		# - compounds (fdotaccent)
		# - ligatures like f_f.(liga.)short
		"""
		pass

	def ssXX2salt(self, saltTag="salt"):
		"""Creates a universal salt feature including all ssXX substitutions."""
		thisFont = Glyphs.font  # frontmost font
		ssXXfeatures = [f for f in thisFont.features if f.name.startswith("ss") and f.name[-1] in "0123456789" and f.name[-2] in "012"]

		if not ssXXfeatures:
			print(u"🤷🏻‍♀️ Warning: no ssXX features found in frontmost font (%s), skipping 'salt'." % thisFont.familyName)
		else:
			print(
				u"✅ Found %i stylistic set%s: %s. Building salt code..." % (
					len(ssXXfeatures),
					"" if len(ssXXfeatures) == 1 else "s",
					", ".join([f.name for f in ssXXfeatures]),
				)
			)
			saltFeature = GSFeature()
			saltFeature.name = saltTag
			saltFeature.automatic = False
			saltFeature.code = ""
			alreadyHadTheFeature = []
			alreadyHadTheLookup = []
			for thisFeature in ssXXfeatures:
				if "lookup" in thisFeature.code:
					if thisFeature.code.strip() not in alreadyHadTheLookup:
						saltFeature.code += "# Lookup code for %s:\n" % thisFeature.name
						saltFeature.code += thisFeature.code
						saltFeature.code += "\n"
						alreadyHadTheLookup.append(thisFeature.code.strip())
				else:
					ssXXcode = ""
					for ssXXline in thisFeature.code.splitlines():
						ssXXcode += "\t%s\n" % ssXXline

					# avoid duplicate lookup names
					ssXXname = thisFeature.name
					i = 0
					while ssXXname in alreadyHadTheFeature:
						i += 1
						ssXXname = "%s_%03i" % (thisFeature.name, i)
					alreadyHadTheFeature.append(ssXXname)

					lookupCode = "lookup salt_%s {\n%s\n} salt_%s;\n\n" % (
						ssXXname,
						ssXXcode.rstrip(),
						ssXXname,
					)
					saltFeature.code += lookupCode

			saltFeature.code = saltFeature.code.strip() + "\n"

			if thisFont.features["salt"] and thisFont.features["salt"].code == saltFeature.code:
				print(u"🤷🏻‍♀️ Feature salt already exists and is up to date, skipping 'salt'.")
			elif saltFeature.code:
				# delete existing salt feature, if there is one:
				if thisFont.features["salt"]:
					saltFeature.notes = "# OLD CODE:\n" + thisFont.features["salt"].code
					del (thisFont.features["salt"])
					print(u"✅ Deleted existing 'salt' feature.")

				# add salt in front of first ssXX:
				i = 0
				# step through features until we can add salt:
				while not thisFont.features["salt"]:
					f = thisFont.features[i]
					# first ssXX feature:
					if f.name == ssXXfeatures[0].name:
						# add the new salt feature in the right spot:
						thisFont.insertObject_inFeaturesAtIndex_(saltFeature, i)
						print(u"✅ Inserted new 'salt' feature in front of first ssXX.")
					i += 1
			else:
				print(u"⛔️ Build salt error: No salt feature code could be assembled. Please check the contents of your ssXX features. Skipping 'salt'.")

	def scFeatureFix(self):
		"""
		MarksCombCase --> MarksComb
		lookup capMarksToSC {
			sub @MarkscombCase by @Markscomb;
		} capMarksToSC;

		jdotless --> j.sc
		idotless --> i.sc
		"""
		thisFont = Glyphs.font
		ccmpFeature = thisFont.features["ccmp"]

		# 1. CAP MARKS IN C2SC
		scFeatureTag = "c2sc"
		if not thisFont.features[scFeatureTag]:
			print(u"⚠️ No %s feature found. Skipping." % scFeatureTag)
		else:
			code = ""
			if ccmpFeature and "@MarkscombCase" in ccmpFeature.code:
				# reuse ccmp classes:
				code = "\tsub @MarkscombCase by @Markscomb;"
			else:
				# TODO or make your own:
				print(u"⚠️ Warning: could not create c2sc code for *comb.case marks (not implemented yet)")
				pass

			if not code:
				print(u"🤷🏻‍♀️ No code could be formed based on the available glyphs. Leaving %s unchanged." % scFeatureTag)
			else:
				# add code to feature:
				updateAndAutodisableFeatureInFont(scFeatureTag, thisFont)
				code = wrapCodeInLookup(code, "capMarksToSC")
				createOTFeature(
					featureName=scFeatureTag,
					featureCode=code,
					targetFont=thisFont,
					codeSig="Prepare cap marks for smallcaps",
					appendCode=False,
					addNote=True,
				)

		# 2. SMCP: SMALL LETTERS WHERE CASEFOLDING CAN OVERLAP WITH OTHERS
		scFeatureTag = "smcp"
		if not thisFont.features[scFeatureTag]:
			print(u"⚠️ No %s feature found. Skipping." % scFeatureTag)
		else:
			code = ""
			casefoldings = {
				"kgreenlandic": "k",
				"idotless": "i",
				"jdotless": "j",
				"longs": "s",
			}
			scSuffixes = ("sc", "smcp", "c2sc", "small", "smallcap")
			for smallGlyphName in sorted(casefoldings.keys()):
				smallGlyph = thisFont.glyphs[smallGlyphName]

				# determine proper .sc glyph:
				correspondingSC = None
				for suffix in scSuffixes:
					if not correspondingSC:
						correspondingSC = thisFont.glyphs["%s.%s" % (smallGlyphName, suffix)]

				# if proper .sc does not exist, casemap it to alternate SC:
				if smallGlyph and smallGlyph.export:
					if not correspondingSC or (correspondingSC and not correspondingSC.export):
						altSCcore = casefoldings[smallGlyphName]
						altSCexists = False
						for suffix in scSuffixes:
							if not altSCexists:
								altSCname = "%s.%s" % (altSCcore, suffix)
								altSC = thisFont.glyphs[altSCname]
								if altSC and altSC.export:
									altSCexists = True
						if altSCexists and altSCname:
							code += "sub %s by %s;\n" % (smallGlyphName, altSCname)
							if thisFont.glyphs["quoteright"]:
								code = code.replace("sub kgreenlandic by %s;" % altSCname, "sub kgreenlandic by %s quoteright;" % altSCname)
							print(u"✅ %s: Adding substitution for %s to %s." % (scFeatureTag, smallGlyphName, altSCname))

			if not code:
				print(u"🤷🏻‍♀️ No code could be formed based on the available glyphs. Leaving %s unchanged." % scFeatureTag)
			else:
				# add code to feature:
				updateAndAutodisableFeatureInFont(scFeatureTag, thisFont)
				createOTFeature(
					featureName=scFeatureTag,
					featureCode=code.rstrip(),
					targetFont=thisFont,
					codeSig="Alternate small-cap mappings",
					appendCode=True,
					addNote=True,
				)

	def FeatureCodeTweaksMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print(u"⚠️ Note: 'Feature Code Tweaks' could not write preferences.")

			# brings macro window to front and clears its log:
			Glyphs.clearLog()

			thisFont = Glyphs.font  # frontmost font
			print(u"Feature Code Tweaks for %s" % thisFont.familyName)
			print(thisFont.filepath)

			# ccmp fi, fl, etc.
			if self.pref("scFeatureFix"):
				print(u"\n- SC Feature Fix")
				self.scFeatureFix()

			# arrows
			if self.pref("addArrowLigs"):
				print(u"\n- Add Arrow Ligs")
				self.addArrowLigs()

			# locl DEU: calt G/germandbls
			if self.pref("germanLocalization"):
				print(u"\n- German Localization")
				self.germanLocalization()

			# locl NLD
			if self.pref("dutchLocalization"):
				print(u"\n- Dutch Localization")
				self.dutchLocalization()

			# SC additions (i/jdotless)
			if self.pref("decomposePresentationForms"):
				print(u"\n- Decompose Presentation Forms")
				self.decomposePresentationForms()

			# short f substitution
			if self.pref("fShortSubstitution"):
				print(u"\n- Add f.short substitutions")
				self.fShortSubstitution()

			# Mag.a
			if self.pref("magistra"):
				print(u"\n- Add Mag.a substitutions")
				self.magistraSubstitution()

			# ssXX to salt
			if self.pref("ssXX2salt"):
				print(u"\n- Add salt feature with ssXX lookups")
				self.ssXX2salt()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(u"❌ Feature Code Tweaks Error: %s" % e)
			import traceback
			print(traceback.format_exc())


FeatureCodeTweaks()
