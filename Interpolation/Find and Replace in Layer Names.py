#MenuTitle: Find and Replace in Layer Names
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Replaces strings in layer names of all selected glyphs. Useful for adjusting layers for the bracket trick: https://glyphsapp.com/learn/alternating-glyph-shapes/
"""

import vanilla

class replaceInLayerNames(object):
	def __init__(self):
		# Window 'self.w':
		windowWidth  = 200
		windowHeight = 130
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Find and Replace in Layer Names", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FindAndReplaceInLayerNames.mainwindow" # stores last window position and size
		)
		
		self.w.textSearch = vanilla.TextBox((15, 15, 67, 14), "Search for:", sizeStyle='small')
		self.w.searchFor = vanilla.EditText((15+67, 12, -15, 19), "[130]", sizeStyle='small', callback=self.SavePreferences)
		
		self.w.textReplace = vanilla.TextBox((15, 15+22, 67, 14), "Replace by:", sizeStyle='small')
		self.w.replaceBy = vanilla.EditText((15+67, 12+22, -15, 19), "[150]", sizeStyle='small', callback=self.SavePreferences)

		self.w.allGlyphs = vanilla.CheckBox( (15, 15+44, -15, 20), "Include all glyphs in font", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.replaceButton = vanilla.Button((-80, -40, -15, -5), "Replace", sizeStyle='small', callback=self.buttonCallback)
		
		self.LoadPreferences()
		
		self.w.setDefaultButton( self.w.replaceButton )
		self.w.open()
		self.w.makeKey()
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.searchFor"] = self.w.searchFor.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.replaceBy"] = self.w.replaceBy.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.allGlyphs"] = self.w.allGlyphs.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInLayerNames.searchFor", "[10]")
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInLayerNames.replaceBy", "[20]")
			Glyphs.registerDefault("com.mekkablue.FindAndReplaceInLayerNames.allGlyphs", True)
			self.w.searchFor.set( Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.searchFor"] )
			self.w.replaceBy.set( Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.replaceBy"] )
			self.w.allGlyphs.set( Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.allGlyphs"] )
		except:
			return False
			
		return True
	
	def buttonCallback(self, sender):
		thisFont = Glyphs.font
		if Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.allGlyphs"]:
			glyphsToProcess = thisFont.glyphs
		else:
			selectedLayers = thisFont.selectedLayers
			glyphsToProcess = [l.parent for l in selectedLayers]
		
		searchFor = Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.searchFor"]
		replaceBy = Glyphs.defaults["com.mekkablue.FindAndReplaceInLayerNames.replaceBy"]
		
		replaceCount = 0

		thisFont.disableUpdateInterface()
		try:
			for thisGlyph in glyphsToProcess:
				for thisLayer in thisGlyph.layers:
					# do not change names of master layers:
					if thisLayer.layerId != thisLayer.associatedFontMaster().id:
						if thisLayer.name is None:
							print("Warning! Empty layer name in: %s" % thisGlyph.name)
						elif searchFor in thisLayer.name:
							thisLayer.name = thisLayer.name.replace( searchFor, replaceBy )
							print("%s: %s" % ( thisGlyph.name, thisLayer.name ))
							replaceCount += 1
		except Exception as e:
			Glyphs.showMacroWindow()
			print("\n⚠️ Script Error:\n")
			import traceback
			print(traceback.format_exc())
			print()
			raise e
		finally:
			thisFont.enableUpdateInterface() # re-enables UI updates in Font View
		
		if replaceCount > 0:
			Message(title="Replaced successfully", message="Replaced %i occurrences."%replaceCount, OKButton=None)
		else:
			Message(title="Nothing replaced", message="Could not find any occurrences of search string in the processed layers.", OKButton=None)
			

replaceInLayerNames()

