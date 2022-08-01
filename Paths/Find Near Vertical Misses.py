#MenuTitle: Find Near Vertical Misses
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Finds nodes that are close but not exactly on vertical metrics.
"""

import vanilla

class FindNearVerticalMisses( object ):
	marker = u"❌"
	heightsToCheck = []
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 510
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Find Near Vertical Misses", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FindNearVerticalMisses.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Find glyphs with nodes not exactly on vertical metrics:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.devianceText = vanilla.TextBox( (inset, linePos+3, inset+135, 14), u"Find nodes off by up to:", sizeStyle='small', selectable=True )
		self.w.deviance = vanilla.EditText( (inset+135, linePos, -inset, 19), "1", callback=self.SavePreferences, sizeStyle='small' )
		self.w.deviance.getNSTextField().setToolTip_(u"Finds nodes that are not equal to the metric, but off up to this value in units. Minimum: 1 unit.")
		linePos += lineHeight
		
		# BOX
		linePos += int(lineHeight//2)
		self.w.whereToCheck = vanilla.Box( (inset, linePos, -inset, int(lineHeight*7.6)) )
		insetLinePos = int(inset*0.2)
		
		self.w.whereToCheck.ascender = vanilla.CheckBox( (int(0.5*inset), insetLinePos-1, -inset, 20), u"Ascender (caps ignored)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.whereToCheck.ascender.getNSButton().setToolTip_(u"Checks if points are not exactly on, but just off the ascender of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight
		
		self.w.whereToCheck.capHeight = vanilla.CheckBox( (int(0.5*inset), insetLinePos-1, -inset, 20), u"Cap Height (lowercase ignored)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.whereToCheck.capHeight.getNSButton().setToolTip_(u"Checks if points are not exactly on, but just off the capHeight of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight
		
		self.w.whereToCheck.shoulderHeight = vanilla.CheckBox( (int(0.5*inset), insetLinePos-1, -inset, 20), u"shoulderHeight (UC, LC, SC ignored)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.whereToCheck.shoulderHeight.getNSButton().setToolTip_(u"Checks if points are not exactly on, but just off the shoulderHeight of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight
		
		self.w.whereToCheck.smallCapHeight = vanilla.CheckBox( (int(0.5*inset), insetLinePos-1, -inset, 20), u"smallCapHeight (only considers smallcaps)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.whereToCheck.smallCapHeight.getNSButton().setToolTip_(u"Checks if points are not exactly on, but just off the smallCapHeight of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight
		
		self.w.whereToCheck.xHeight = vanilla.CheckBox( (int(0.5*inset), insetLinePos-1, -inset, 20), u"x-height (caps ignored)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.whereToCheck.xHeight.getNSButton().setToolTip_(u"Checks if points are not exactly on, but just off the xHeight of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight
		
		self.w.whereToCheck.baseline = vanilla.CheckBox( (int(0.5*inset), insetLinePos-1, -inset, 20), u"Baseline", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.whereToCheck.baseline.getNSButton().setToolTip_(u"Checks if points are not exactly on, but just off the baseline of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight
		
		self.w.whereToCheck.descender = vanilla.CheckBox( (int(0.5*inset), insetLinePos-1, -inset, 20), u"Descender", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.whereToCheck.descender.getNSButton().setToolTip_(u"Checks if points are not exactly on, but just off the descender of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight
		
		linePos += lineHeight
		# BOX END
		
		self.w.tolerateIfNextNodeIsOn = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Tolerate near miss if next node is on", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.tolerateIfNextNodeIsOn.getNSButton().setToolTip_("Will skip the just-off node if the next or previous on-curve node is EXACTLY on the metric line. Useful if you have very thin serifs or short segments near the metric lines.")
		linePos += lineHeight
		
		self.w.tolerateIfExtremum = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Tolerate near miss for left/right curve extremum", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.tolerateIfExtremum.getNSButton().setToolTip_("Will skip the just-off node if the next and previous nodes are VERTICAL OFF-CURVES. Recommended for avoiding false positives.")
		linePos += lineHeight
		
		
		self.w.includeHandles = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include off-curve points", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeHandles.getNSButton().setToolTip_(u"Also checks BCPs (Bézier control points), vulgo ‘handles’. Otherwise only considers on-curve nodes")
		linePos += lineHeight
		
		self.w.removeOverlap = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Check outlines after Remove Overlap (slower)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.removeOverlap.getNSButton().setToolTip_(u"Only checks outlines after overlap removal. That way, ignores triangular overlaps (‘opened corners’). Use this option if you have too many false positives.")
		linePos += lineHeight
		
		self.w.markNodes = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Mark affected nodes with %s"%self.marker, value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.markNodes.getNSButton().setToolTip_(u"Sets the name of affected nodes to this emoji, so you can easily find it. ATTENTION: If Remove Overlap option is on, will use the emoji as an annotation instead.")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_(u"Also check for near misses in glyphs that are set to not export. Useful if you are using non-exporting parts as components in other glyphs.")
		linePos += lineHeight
		
		self.w.includeComposites = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include composites", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeComposites.getNSButton().setToolTip_(u"If unchecked, will only go through glyphs that have paths in them. Recommended to leave off, because it usually reports a lot of false positives.")
		linePos += lineHeight
		
		self.w.excludeText = vanilla.TextBox( (inset, linePos+3, 150, 14), u"Exclude glyphs containing:", sizeStyle='small', selectable=True )
		self.w.exclude = vanilla.EditText( (inset+150, linePos, -inset, 19), ".ornm, .notdef, comb", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.openTab = vanilla.CheckBox( (inset, linePos-1, 190, 20), u"Open tab with affected layers", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openTab.getNSButton().setToolTip_(u"If it finds nodes just off the indicated metrics, will open a new tab with the layers if found the deviating nodes on. Otherwise please check the detailed report in Macro Window.")
		self.w.reuseTab = vanilla.CheckBox( (inset+190, linePos-1, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reuseTab.getNSButton().setToolTip_(u"If a tab is open already, will use that one, rather than opening a new tab. Recommended, keeps tab clutter low.")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.FindNearVerticalMissesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Status Message:
		self.w.status = vanilla.TextBox( (inset, -18-inset, -80-inset, 14), u"🤖 Ready.", sizeStyle='small', selectable=True )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Find Near Vertical Misses' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.exclude"]= self.w.exclude.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.markNodes"]= self.w.markNodes.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeNonExporting"]= self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeHandles"]= self.w.includeHandles.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.descender"]= self.w.whereToCheck.descender.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.baseline"]= self.w.whereToCheck.baseline.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.xHeight"]= self.w.whereToCheck.xHeight.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.smallCapHeight"]= self.w.whereToCheck.smallCapHeight.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.shoulderHeight"]= self.w.whereToCheck.shoulderHeight.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.capHeight"]= self.w.whereToCheck.capHeight.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.ascender"]= self.w.whereToCheck.ascender.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.deviance"]= self.w.deviance.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.tolerateIfNextNodeIsOn"]= self.w.tolerateIfNextNodeIsOn.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.tolerateIfExtremum"]= self.w.tolerateIfExtremum.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.removeOverlap"]= self.w.removeOverlap.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeComposites"]= self.w.includeComposites.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.openTab"]= self.w.openTab.get()
			Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.reuseTab"]= self.w.reuseTab.get()
			
			self.checkGUI()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.deviance", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.exclude", ".ornm, .notdef, comb")
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.markNodes", 0)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.includeNonExporting", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.includeHandles", 0)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.descender", 0)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.baseline", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.xHeight", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.smallCapHeight", 0)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.shoulderHeight", 0)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.capHeight", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.ascender", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.tolerateIfNextNodeIsOn", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.tolerateIfExtremum", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.removeOverlap", 0)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.includeComposites", 0)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.openTab", 1)
			Glyphs.registerDefault("com.mekkablue.FindNearVerticalMisses.reuseTab", 1)
		
						
			self.w.deviance.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.deviance"] )
			self.w.exclude.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.exclude"] )
			self.w.markNodes.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.markNodes"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeNonExporting"] )
			self.w.includeHandles.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeHandles"] )
			self.w.tolerateIfNextNodeIsOn.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.tolerateIfNextNodeIsOn"] )
			self.w.tolerateIfExtremum.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.tolerateIfExtremum"] )
			self.w.removeOverlap.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.removeOverlap"] )
			self.w.includeComposites.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeComposites"] )
			self.w.openTab.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.openTab"] )
			self.w.reuseTab.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.reuseTab"] )
			
			self.w.whereToCheck.descender.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.descender"] )
			self.w.whereToCheck.baseline.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.baseline"] )
			self.w.whereToCheck.xHeight.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.xHeight"] )
			self.w.whereToCheck.smallCapHeight.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.smallCapHeight"] )
			self.w.whereToCheck.shoulderHeight.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.shoulderHeight"] )
			self.w.whereToCheck.capHeight.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.capHeight"] )
			self.w.whereToCheck.ascender.set( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.ascender"] )
			
			self.checkGUI()
		except:
			return False
			
		return True
	
	def checkGUI(self, sender=None):
		# At least one vertical metrics must be on, otherwise disable button:
		enableButton = False
		boxDict = self.w.whereToCheck.__dict__
		for itemName in boxDict:
			checkbox = boxDict[itemName]
			if type(checkbox) == vanilla.vanillaCheckBox.CheckBox:
				if checkbox.get():
					enableButton = True
					break
		self.w.runButton.enable(onOff=enableButton)
		
		# disable Reuse Tab button if Open Tab is off:
		self.w.reuseTab.enable(self.w.openTab.get())
		
	
	def isNodeSlightlyOff(self, nodePosition, master, deviance, prevY, nextY, glyphType=None, glyphSuffix=None):
		y = nodePosition.y
		prevAndNextDontCount = prevY is None or nextY is None
		
		if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.descender"]:
			if y != master.descender:
				if master.descender-deviance <= y <= master.descender+deviance:
					if prevAndNextDontCount or (prevY != master.descender and nextY != master.descender):
						return True
					else:
						# prev or next node or exactly on metric line, so do not count as off:
						return False
					
		if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.baseline"]:
			if y != 0.0:
				if 0.0-deviance <= y <= 0.0+deviance:
					if prevAndNextDontCount or (prevY != 0.0 and nextY != 0.0):
						return True
					else:
						# prev or next node or exactly on metric line, so do not count as off:
						return False
					
		if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.xHeight"]:
			if glyphType is None or not glyphType in ("Uppercase","Smallcaps"):
				if y != master.xHeight:
					if master.xHeight-deviance <= y <= master.xHeight+deviance:
						if prevAndNextDontCount or (prevY != master.xHeight and nextY != master.xHeight):
							return True
						else:
							# prev or next node or exactly on metric line, so do not count as off:
							return False
					
		if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.smallCapHeight"]:
			suffixIsSC = False
			if glyphSuffix:
				suffixes = glyphSuffix.split(".") # could be multiple suffixes
				for suffix in ("sc","smcp","c2sc"):
					 if suffix in suffixes:
						 suffixIsSC = True
						 
			if suffixIsSC or glyphType == "Smallcaps": # is smallcap
				smallCapHeight = master.customParameters["smallCapHeight"]
				if smallCapHeight:
					smallCapHeight = float(smallCapHeight)
					if y != smallCapHeight:
						if smallCapHeight-deviance <= y <= smallCapHeight+deviance:
							if prevAndNextDontCount or (prevY != smallCapHeight and nextY != smallCapHeight):
								return True
							else:
								# prev or next node or exactly on metric line, so do not count as off:
								return False
					
		if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.shoulderHeight"]:
			if glyphType is None or not glyphType in ("Lowercase","Uppercase","Smallcaps"):
				shoulderHeight = master.customParameters["shoulderHeight"]
				if shoulderHeight:
					shoulderHeight = float(shoulderHeight)
					if y != shoulderHeight:
						if shoulderHeight-deviance <= y <= shoulderHeight+deviance:
							if prevAndNextDontCount or (prevY != shoulderHeight and nextY != shoulderHeight):
								return True
							else:
								# prev or next node or exactly on metric line, so do not count as off:
								return False
					
		if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.capHeight"]:
			if glyphType is None or not glyphType in ("Lowercase","Smallcaps"):
				if y != master.capHeight:
					if master.capHeight-deviance <= y <= master.capHeight+deviance:
						if prevAndNextDontCount or (prevY != master.capHeight and nextY != master.capHeight):
							return True
						else:
							# prev or next node or exactly on metric line, so do not count as off:
							return False
					
		if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.ascender"]:
			if glyphType is None or not glyphType in ("Uppercase","Smallcaps"):
				if y != master.ascender:
					if master.ascender-deviance <= y <= master.ascender+deviance:
						if prevAndNextDontCount or (prevY != master.ascender and nextY != master.ascender):
							return True
						else:
							# prev or next node or exactly on metric line, so do not count as off:
							return False
		
		return False
		
	def doubleCheckNodeName(self, thisNode):
		if thisNode.name == self.marker:
			thisNode.name = None
	
	def doubleCheckAnnotations(self, thisLayer):
		for i in range(len(thisLayer.annotations))[::-1]:
			if thisLayer.annotations[i].text == self.marker:
				del thisLayer.annotations[i]
	
	def addAnnotation(self, layer, position, text):
		marker = GSAnnotation()
		marker.type = TEXT
		marker.position = position
		marker.text = text
		marker.width = min( max(50.0, 7*len(text)), 600.0 ) # min=50, max=600
		layer.annotations.append(marker)
		
	def FindNearVerticalMissesMain( self, sender ):
		try:
			# clears macro window log:
			Glyphs.clearLog()
			self.w.progress.set(0)
			
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Find Near Vertical Misses' could not write preferences.")
			
			self.checkGUI()
			
			thisFont = Glyphs.font # frontmost font
			print("Find Near Vertical Misses Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			includeComposites = Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeComposites"]
			includeNonExporting = Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeNonExporting"]
			
			deviance = float( Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.deviance"] )
			excludes = [ x.strip() for x in Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.exclude"].split(",") ]
			skippedGlyphs = []
			
			affectedLayers = []
			totalNumberOfGlyphs = len(thisFont.glyphs)
			for i, thisGlyph in enumerate(thisFont.glyphs):
				self.w.progress.set(100*i//totalNumberOfGlyphs)

				glyphIsExcluded = not (thisGlyph.export or includeNonExporting)
				if not glyphIsExcluded:
					for excludedText in excludes:
						if excludedText in thisGlyph.name:
							skippedGlyphs.append(thisGlyph.name)
							glyphIsExcluded = True
							break
				
				if not glyphIsExcluded:
					self.w.status.set("🔠 %s" % thisGlyph.name)
					suffix = None
					if "." in thisGlyph.name:
						offset = thisGlyph.name.find(".")
						suffix = thisGlyph.name[offset:]
						
					for thisLayer in thisGlyph.layers:
						# get rid of debris from previous iterations:
						self.doubleCheckAnnotations(thisLayer)
						layerCounts = thisLayer.isMasterLayer or thisLayer.isSpecialLayer
						layerShouldBeChecked = len(thisLayer.paths)>0 or includeComposites
						
						if layerCounts and layerShouldBeChecked:
							
							# overlap removal if requested:
							if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.removeOverlap"]:
								checkLayer = thisLayer.copyDecomposedLayer()
								checkLayer.removeOverlap()
							else:
								checkLayer = thisLayer
							
							# step through nodes:
							for thisPath in checkLayer.paths:
								for thisNode in thisPath.nodes:
									nodeIsOncurve = thisNode.type != OFFCURVE
									if nodeIsOncurve or Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.includeHandles"]:
										
										skipThisNode = False
										if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.tolerateIfExtremum"]:
											if thisNode.prevNode:
												if thisNode.prevNode.type == OFFCURVE and thisNode.nextNode.type == OFFCURVE:
													vertical = thisNode.x == thisNode.prevNode.x == thisNode.nextNode.x
													linedUp = (thisNode.y-thisNode.prevNode.y)*(thisNode.nextNode.y-thisNode.y) > 0.0
													if vertical and linedUp:
														skipThisNode = True
											else:
												print("⚠️ Potential open path in %s" % thisGlyph.name)
										
										if not skipThisNode:
											if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.tolerateIfNextNodeIsOn"]:
												# determine previous oncurve point
												previousOnCurve = thisNode.prevNode
												if previousOnCurve:
													while previousOnCurve.type == OFFCURVE:
														previousOnCurve = previousOnCurve.prevNode
													previousY = previousOnCurve.y
													# determine next oncurve point
													nextOnCurve = thisNode.nextNode
													while nextOnCurve.type == OFFCURVE:
														nextOnCurve = nextOnCurve.nextNode
													nextY = nextOnCurve.y
												else:
													print("⚠️ Potential open path in %s" % thisGlyph.name)
											else:
												previousY = None
												nextY = None
											
											glyphType = None
											if Glyphs.versionNumber >= 3:
												# GLYPHS 3
												if thisGlyph.case == GSUppercase:
													glyphType = "Uppercase"
												elif thisGlyph.case == GSLowercase:
													glyphType = "Lowercase"
												elif thisGlyph.case == GSSmallcaps:
													glyphType = "Smallcaps"
											else:
												glyphType = thisGlyph.subCategory
											
											if self.isNodeSlightlyOff( thisNode.position, thisLayer.master, deviance, previousY, nextY, glyphType, suffix ):
												# collect layer:
												if not thisLayer in affectedLayers:
													affectedLayers.append(thisLayer)
												thisNode.selected = True

												# report:
												print(u"%s /%s '%s': %.1f %.1f" % (self.marker, thisGlyph.name, thisLayer.name, thisNode.x, thisNode.y))

												# node name:
												if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.markNodes"]:
													if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.removeOverlap"]:
														self.addAnnotation(thisLayer, thisNode.position, self.marker)
													else:
														thisNode.name = self.marker
												else:
													self.doubleCheckNodeName(thisNode)
											else:
												self.doubleCheckNodeName(thisNode)
									else:
										self.doubleCheckNodeName(thisNode)
			
			
			# Done. Set Progress Bar to max and report:
			
			self.w.progress.set(100)
			self.w.status.set("✅ Done.")
			
			if skippedGlyphs:
				print()
				print(u"Skipped glyphs:\n%s" % ", ".join(skippedGlyphs))
			
			print() 
			print("Done.")
			
			if affectedLayers:
				if Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.openTab"]:
					# try to reuse current tab:
					resultTab = thisFont.currentTab
					if resultTab and Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.reuseTab"]:
						resultTab.layers = ()
					else:
						# open new tab:
						resultTab = thisFont.newTab()
					resultTab.layers = affectedLayers
				else:
					# brings macro window to front:
					Glyphs.showMacroWindow()
			else:
				Message(
					title="No Deviant Nodes", 
					message=u"Congratulations! No nodes found missing the indicated metrics and off by up to %s u." % Glyphs.defaults["com.mekkablue.FindNearVerticalMisses.deviance"], 
					OKButton=u"🥂Cheers!")
					
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Find Near Vertical Misses Error: %s" % e)
			import traceback
			print(traceback.format_exc())

FindNearVerticalMisses()