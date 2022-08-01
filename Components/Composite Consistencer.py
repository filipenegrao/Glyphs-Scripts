#MenuTitle: Composite Consistencer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Goes through all glyphs of the frontmost font, and checks for composites in the current master. If dot-suffixed glyph variants are missing them, they are reported in the Macro Window.
"""

import vanilla
defaultSuffixes = ".dnom, .numr, .subs, .sups, .sinf, .case, .tf, .tosf, .osf"

def normalizedSuffixOrder(name):
	particles = name.split(".")
	if len(particles) > 1:
		particles =  [particles[0]] + sorted(particles[1:])
		name = ".".join(particles)
	return name

class CompositeConsistencer( object ):
	prefID = "com.mekkablue.CompositeConsistencer"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 160
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Composite Consistencer", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Find missing suffixed composites:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.ignoreText = vanilla.TextBox( (inset, linePos+3, 90, 14), "Ignore suffixes:", sizeStyle='small', selectable=True )
		self.w.ignore = vanilla.EditText( (inset+90, linePos, -inset, 19), defaultSuffixes, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.ignoreDuplicateSuffixes = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Ignore duplicate suffixes (.ss01.ss01)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.suffixOrderMatters = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Order of suffixes matters (.case.ss01 and .ss01.case)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.CompositeConsistencerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Composite Consistencer' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("ignore")] = self.w.ignore.get()
			Glyphs.defaults[self.domain("ignoreDuplicateSuffixes")] = self.w.ignoreDuplicateSuffixes.get()
			Glyphs.defaults[self.domain("suffixOrderMatters")] = self.w.suffixOrderMatters.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("ignore"), defaultSuffixes)
			Glyphs.registerDefault(self.domain("ignoreDuplicateSuffixes"), True)
			Glyphs.registerDefault(self.domain("suffixOrderMatters"), False)
			
			# load previously written prefs:
			self.w.ignore.set( self.pref("ignore") )
			self.w.ignoreDuplicateSuffixes.set( self.pref("ignoreDuplicateSuffixes") )
			self.w.suffixOrderMatters.set( self.pref("suffixOrderMatters") )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def CompositeConsistencerMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Composite Consistencer' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Composite Consistencer Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
			
				thisMaster = thisFont.selectedFontMaster
				allNames = [g.name for g in thisFont.glyphs if g.export]
				
				ignore = self.pref("ignore")
				ignoredSuffixes = [s.strip().strip(".") for s in ignore.split(",")]
				ignoreDuplicateSuffixes = self.pref("ignoreDuplicateSuffixes")
				suffixOrderMatters = self.pref("suffixOrderMatters")
				if not suffixOrderMatters:
					allNames = [normalizedSuffixOrder(n) for n in allNames]
				
				countAffectedGlyphs = 0
				countMissingComposites = 0
				for thisGlyph in thisFont.glyphs:
					thisGlyphAffected = False
					composites = thisFont.glyphsContainingComponentWithName_masterId_(thisGlyph.name, thisMaster.id)
					if composites:
						compositeNames = [g.name for g in composites]
						if not suffixOrderMatters:
							compositeNames = [normalizedSuffixOrder(n) for n in compositeNames]
						for otherName in allNames:
							if otherName.startswith(thisGlyph.name + "."):
								otherSuffix = otherName[len(thisGlyph.name)+1:]
								if all([not s in otherSuffix.split(".") for s in ignoredSuffixes]):
									missingOtherNames = []
									for thisCompositeName in compositeNames:
										otherCompositeName = "%s.%s" % (thisCompositeName.rstrip("."), otherSuffix.strip("."))
										if not suffixOrderMatters:
											otherCompositeName = normalizedSuffixOrder(otherCompositeName)
										if not otherCompositeName in allNames:
											if not ignoreDuplicateSuffixes or len(otherCompositeName.split(".")[1:])==len(set(otherCompositeName.split(".")[1:])):
												missingOtherNames.append(otherCompositeName)
									if missingOtherNames:
										countMissingComposites += len(missingOtherNames)
										if not thisGlyphAffected:
											countAffectedGlyphs += 1
											thisGlyphAffected = True
										print("%s is missing %i composite%s:\n%s\n" % (
											otherName, 
											len(missingOtherNames),
											"" if len(missingOtherNames)==1 else "s",
											", ".join(missingOtherNames),
											))

			# Final report:
			Glyphs.showNotification( 
				"%s: %i glyph%s missing composites" % (
					thisFont.familyName,
					countAffectedGlyphs, "" if countAffectedGlyphs==1 else "s",
					),
				"%i glyph%s missing %i composite%s. Details in Macro Window" % (
					countAffectedGlyphs, "" if countAffectedGlyphs==1 else "s",
					countMissingComposites, "" if countMissingComposites==1 else "s",
				),
				)
			if not suffixOrderMatters:
				print("\n⚠️ Attention: the displayed suffix order may not be intended.")
			print("Done.")

			# brings macro window to front:
			Glyphs.showMacroWindow()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Composite Consistencer Error: %s" % e)
			import traceback
			print(traceback.format_exc())

CompositeConsistencer()