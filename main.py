# This file must be named main.py for it to function in android!
import pygame
import math
###import PIL.Image
import os.path
import json
# Import the android module. If we can't import it, set it to None - this
# lets us test it, and check to see if we want android-specific behavior.
try:
    import android
except ImportError:
    android = None



class Tile: 
    tileSize = 0
    height = 0
    
    def __init__(self, img, idx, tileSize, x, y):
        self.image = img
        self.index = idx
        self.windowX1 = x
        self.windowY1 = y
        Tile.tileSize = tileSize
     
    def setReflection(self, r):
        if r not in ["windowX1", "windowY1"]:
            print "reflection value must be 'windowX1' or 'windowY1'"
        else:
            self.reflection = r 
      
    def setRotation(self, r):
        if (r % 90) not in [0, 1, 2, 3]:
            print "rotation value must be 0 to 270 degrees"
        else:
            self.rotation = r  
        
    def getSize(self):
        return Tile.tileSize  
    
    def getImage(self):
        return self.image
    
    def getXY(self):
        return self.windowX1, self.windowY1
    
    def getX(self):
        return self.windowX1
    
    def getY(self):
        return self.windowY1 
    
    def getIndex(self):
        return self.index



class Model:
    def __init__ (self, screen, xTiles, yTiles, tileSize):
        self.screen = screen
        screenRect = screen.get_rect()
        #create two screen views for tileSet and tileMap
        tileSetWindowFactor = 4
        tsvWidth = screenRect.width / tileSetWindowFactor
        tsvHeight = screenRect.height
        tmvWidth = screenRect.width - tsvWidth
        self.tileSetView = screen.subsurface( (0, 0), (tsvWidth, tsvHeight) )
        self.tileMapView = screen.subsurface( (tsvWidth, 0),(tmvWidth, tsvHeight) )
        self.tileSetViewRect = self.tileSetView.get_rect()
        self.tileMapViewRect = self.tileMapView.get_rect()
        #import a tileSet image---
        self.tileSetArr = Model.loadTileSetImage(self, tileSize, "tileSet.png")
        #create array for tileMap
        ###img = PIL.Image.new("RGBA", (tileSize, tileSize))
        ###tileSurf = pygame.image.fromstring(img.tostring(), img.size, img.mode)
        self.defaultTile = Tile(None, None, tileSize, None, None)   #change first argument to tileSurf later
        self.tileMapArr = [self.defaultTile] * 10
        self.tileMapArr = []
        for i in range(xTiles):
            self.tileMapArr.append([self.defaultTile] * yTiles)
        #menu related-----
        self.menuRect = pygame.Rect((0 ,0), (screenRect.width, 96))
        self.saveButton = pygame.Rect(16, 16, 96, 64)
        self.saveActive = False
        #scrolling related----       
        self.scrollThickness = 30
        self.trackX1 = pygame.Rect(self.tileSetViewRect.left, 
                                   self.tileSetViewRect.bottom - self.scrollThickness, 
                                   self.tileSetViewRect.width, 
                                   self.scrollThickness)
        self.trackY1 = pygame.Rect(self.tileSetViewRect.width - self.scrollThickness, 
                                   self.tileSetViewRect.top + self.menuRect.height, 
                                   self.scrollThickness, 
                                   self.tileSetViewRect.height - self.menuRect.height)
        self.trackX2 = pygame.Rect(self.tileMapViewRect.left, 
                                   self.tileMapViewRect.bottom - self.scrollThickness, 
                                   self.tileMapViewRect.width, 
                                   self.scrollThickness)
        self.trackY2 = pygame.Rect(self.tileMapViewRect.width - self.scrollThickness, 
                                   self.tileMapViewRect.top + self.menuRect.height, 
                                   self.scrollThickness, 
                                   self.tileMapViewRect.height - self.menuRect.height)
        #tileSet sliderBar's flags and properties     
        self.slideX1 = pygame.Rect(self.trackX1)
        self.slideX1.width = self.trackX1.width / 3  
        self.scrollingX1 = False #false when not scrolling
        self.slideY1 = pygame.Rect(self.trackY1)  
        self.slideY1.height = self.trackY1.height / 4  
        self.scrollingY1 = False
        #tileMap slideBar's flags and properties
        self.slideX2 = pygame.Rect(self.trackX2)
        self.slideX2.width = self.trackX2.width / 3  
        self.scrollingX2 = False #false when not scrolling
        self.slideY2 = pygame.Rect(self.trackY2)  
        self.slideY2.height = self.trackY2.height / 4  
        self.scrollingY2 = False
        #create tiletable surfaces
        rows = len(self.tileSetArr)
        cols = len(self.tileSetArr[0])
        self.tileSize = tileSize
        tileSetWidth = rows * tileSize
        tileSetHeight = cols * tileSize
        tileMapWidth = xTiles * tileSize
        tileMapHeight = yTiles * tileSize
        if tileSetHeight < self.trackY1.height - self.scrollThickness:  #adjust tileSet dimensions if too small 
            tileSetHeight = self.trackY1.height - self.scrollThickness
        if tileSetHeight < self.trackX1.width - self.scrollThickness:
            tileSetHeight = self.trackX1.width - self.scrollThickness
        if tileMapHeight < self.trackY2.height - self.scrollThickness:
            tileMapHeight = self.trackY2.height - self.scrollThickness
        if tileMapWidth < self.trackX2.width - self.scrollThickness:
            tileMapWidth = self.trackX2.width - self.scrollThickness
        self.tileSet = pygame.Surface((tileSetWidth, tileSetHeight),
                                      pygame.SRCALPHA)
        self.tileMap = pygame.Surface((tileMapWidth, tileMapHeight), 
                                      pygame.SRCALPHA)
        #tileSet window related----
        self.windowX1 = 0.0  #window's position in float
        self.windowY1 = 0
        self.windowTileX1 = 0    #window's position in tile format
        self.windowTileY1 = 0 
        #tileMap window related---
        self.windowX2 = 0 #window's position in float
        self.windowY2 = 0
        self.windowTileX2 = 0    #window's position in tile format
        self.windowTileY2 = 0 
        #mouse related-----  
        self.clickX = 0 #stores mouse click position
        self.clickY = 0
        #tile memory
        self.drewTileX = None  #stores last drawn tile position
        self.drewTileY = None
        #draw background only once to lower FPS
        DGRAY = (100, 100, 100)
        self.tileSet.fill(DGRAY)
        self.tileMap.fill(DGRAY)
        #set first run flag
        self.firstRun = True
        #set selected tile
        self.selectedTile = self.defaultTile
        self.newTileSelected = False
        
    def update(self):
        #set tileSetView coordinates
        x1Min = 0
        x1Max = self.trackX1.width - self.scrollThickness
        y1Min = self.menuRect.bottom
        y1Max = y1Min + self.trackY1.height - self.scrollThickness
        
        #set tileMapView coordinates
        x2Min = self.trackX1.width
        x2Max = self.screen.get_width() - self.scrollThickness
        y2Min = self.menuRect.bottom
        y2Max = y2Min + self.trackY2.height - self.scrollThickness
        
        #begin updates..
        if ((self.clickX > x1Min and self.clickX < x1Max and    #tileSet related
            self.clickY > y1Min and self.clickY < y1Max) or
            self.getScrollX1State() or self.getScrollY1State() or self.firstRun):
            #----------------------
            self.findSelectedTile()
            self.updateTileSet()
            self.updateGrid(self.tileSet, self.trackX1, self.trackY1, self.windowX1, self.windowY1)

        if (self.clickX > x2Min and self.clickX < x2Max and     #tileMap related
            self.clickY > y2Min and self.clickY < y2Max and
            not self.getScrollX2State() and not self.getScrollY2State() and
            not self.getScrollX1State() and not self.getScrollY1State()):
            #-------------------
            self.updateTileMap()
            self.updateGrid(self.tileMap, self.trackX2, self.trackY2, self.windowX2, self.windowY2)
            #reset newTileSelected variable
            self.newTileSelected = False
            
        elif self.getScrollX2State() or self.getScrollY2State() or self.firstRun:   #tileMap grid related
            #refresh grid for tileMap surface
            self.updateGrid(self.tileMap, self.trackX2, self.trackY2, self.windowX2, self.windowY2)
         
        #begin drawing to screen..
        self.drawTileSetView()
        self.drawTileMapView()
        self.drawTileHighlight()
        self.drawFrame()
        
        #save tileMap to file "tileMapSave" if save state is enabled
        if self.getSaveActive():
            self.saveTileMap()
        
        if self.firstRun == True:
            self.firstRun = False
    
    def findSelectedTile(self):
        #set mouse to tile translation
        relClickX = self.clickX + self.windowX1  #relative clicks to current window position
        relClickY = self.clickY + self.windowY1
        tileX = math.trunc(relClickX / self.tileSize)   #convert to the nearest upper left portion of tile in grid
        tileY = math.trunc(relClickY / self.tileSize) 
        
        #return selected tile
        if (self.firstRun == False and
            tileX < len(self.tileSetArr) and
            tileY < len(self.tileSetArr[0]) and
            self.selectedTile != self.tileSetArr[tileX][tileY] and #if the same tile is not selected
           self.getScrollX1State() == False and
           self.getScrollY1State() == False and
           self.getScrollX2State() == False and
           self.getScrollY2State() == False):
            self.selectedTile = self.tileSetArr[tileX][tileY]
            self.newTileSelected = True
     
    def updateTileSet(self):    
        #range values
        xMin = self.windowTileX1 / self.tileSize
        xMax = xMin + self.trackX1.width / self.tileSize
        xMax += 2   #draw out of view to prevent view lag
        yMin = self.windowTileY1 / self.tileSize
        yMax = yMin + self.trackY1.height / self.tileSize  #same as above
        yMax += 4   #draw out of view to prevent view lag
        tile = pygame.image
        #cap growth of Max values (used to render past view without producing values beyond array indexes
        if xMax >= len(self.tileSetArr) - 1:
            xMax = len(self.tileSetArr)
        if yMax >= len(self.tileSetArr[0]) - 1:
            yMax = len(self.tileSetArr[0])
        if yMin < 0:
            yMin = 0
        #draw tiles to tileSet surface
        for i in range(xMin, xMax):
            for j in range(yMin, yMax):
                tile = self.tileSetArr[i][j]
                h = w = tile.getSize()
                self.tileSet.blit(tile.getImage(), (i*w, j*h))   
                
    def updateTileMap(self):
        relClickX = self.clickX + self.windowX2 - self.tileSetViewRect.width  #relative clicks to current window position
        relClickY = self.clickY + self.windowY2
        tileX = math.trunc(relClickX / self.tileSize)   #convert to the nearest upper left portion of tile in grid
        tileY = math.trunc(relClickY / self.tileSize) 
        #load tile to draw on Map         
        tile = self.selectedTile
        #draw tile to Map
        if ((self.drewTileX != tileX or self.drewTileY != tileY or self.newTileSelected) and #don't draw to same tile until at least exited unless a new tile is selected
            tileX < len(self.tileMapArr) and    #do not draw outside of predefined tile area
            tileY < len(self.tileMapArr[0]) and
           self.getScrollX1State() == False and
           self.getScrollY1State() == False and
           self.getScrollX2State() == False and
           self.getScrollY2State() == False and
           tile.getImage() != None):    #if the user has not selected a tile from tileset do not draw
            #---do stuff---
            self.tileMapArr[tileX][tileY] = tile   #save tile to map array
            self.tileMap.blit(tile.getImage(), (tileX * self.tileSize, tileY * self.tileSize))
            self.drewTileX = tileX
            self.drewTileY = tileY 

    def updateGrid(self, surf, trackX, trackY, windowX, windowY):
        GRAY = (150, 150, 150)
        windowTileX = math.trunc(windowX / self.tileSize) * self.tileSize
        windowTileY = math.trunc(windowY / self.tileSize) * self.tileSize
        viewWidth = trackX.width - self.scrollThickness
        viewHeight = trackY.height - self.scrollThickness
        viewWidth += 8 * self.tileSize   #render beyond screen to prevent visible lag
        viewHeight += 8 * self.tileSize

        #load grid---------------------
        for i in range(windowTileX, windowTileX + viewWidth, self.tileSize): # draw vertical lines
            pygame.draw.line(surf, GRAY, (i, windowY), (i, windowY + viewHeight)) 
        for j in range(windowTileY, windowTileY + viewHeight, self.tileSize): # draw vertical lines
            pygame.draw.line(surf, GRAY, (windowX, j), (windowX + viewWidth, j))    
                 
    def drawTileSetView(self):  
        #load scrollbar data for tileset-------------- 
        tileSetRect = self.tileSet.get_rect()
        x1Viewable = self.trackX1.width - self.scrollThickness
        x1Scrollable = x1Viewable - self.slideX1.width
        x1Factor = (1.0 * tileSetRect.width - x1Viewable) / x1Scrollable
        tileSetX = self.slideX1.left * x1Factor
        
        y1Viewable = self.trackY1.height - self.scrollThickness
        y1Scrollable = y1Viewable - self.slideY1.height
        y1Factor = (1.0 * tileSetRect.height - y1Viewable) / y1Scrollable
        tileSetY = (self.slideY1.top - self.menuRect.height) * y1Factor - self.menuRect.height
 
        #load scrollbar data for window positions---------------
        tileMapRect = self.tileMap.get_rect()
        x2Viewable = self.trackX2.width - self.scrollThickness
        x2Scrollable = x2Viewable - self.slideX2.width #width of scrollable area relative to leftside of slider
        x2Factor = (1.0 * tileMapRect.width - x2Viewable) / x2Scrollable
        tileMapX = self.slideX2.left * x2Factor
        
        y2Viewable = self.trackY2.height - self.scrollThickness
        y2Scrollable = y2Viewable - self.slideY2.height
        y2Factor = (1.0 * tileMapRect.height - y2Viewable) / y2Scrollable
        tileMapY = (self.slideY2.top - self.menuRect.height) * y2Factor - self.menuRect.height
        
        #set window positions
        self.setWindow1Pos(tileSetX, tileSetY)
        self.setWindow2Pos(tileMapX, tileMapY)

        #draw tileSet 
        self.tileSetView.blit(self.tileSet, (tileSetX * -1, tileSetY * -1) )
        
    def drawTileMapView(self):
        GRAY = (100,100,100)
        #load scrollbar data for window positions---------------
        tileMapRect = self.tileMap.get_rect()
        x2Viewable = self.trackX2.width - self.scrollThickness
        x2Scrollable = x2Viewable - self.slideX2.width #width of scrollable area relative to leftside of slider
        x2Factor = (1.0 * tileMapRect.width - x2Viewable) / x2Scrollable
        tileMapX = self.slideX2.left * x2Factor
        
        y2Viewable = self.trackY2.height - self.scrollThickness
        y2Scrollable = y2Viewable - self.slideY2.height
        y2Factor = (1.0 * tileMapRect.height - y2Viewable) / y2Scrollable
        tileMapY = (self.slideY2.top - self.menuRect.height) * y2Factor - self.menuRect.height
        
        #draw tileMap with dynamic transparency area
        self.tileMapView.blit(self.tileMap, (tileMapX * -1, tileMapY * -1) )     
              
    def drawTileHighlight(self):
        if self.selectedTile.getX() != None and self.selectedTile.getY() != None:
            x = self.selectedTile.getX() * self.tileSize - self.windowX1
            y = self.selectedTile.getY() * self.tileSize - self.windowY1
            if x < self.trackY1.left:
                tileRect = pygame.Rect(1, 1, self.tileSize + 1, self.tileSize + 1) #size of tileMap view
                tileSurf = pygame.Surface( (self.tileSize, self.tileSize),  pygame.SRCALPHA)
                pygame.draw.rect(tileSurf, (0, 200, 255, 100), tileRect, 0)
                self.tileSetView.blit(tileSurf, (x, y))    
        
    def drawFrame(self):
        DGRAY = (80, 80, 70)  
        WHITE = (255, 255, 250)
        GRAY = (160, 160, 160)
        SAVE = (185, 185, 185)
        SAVEIN = (60, 60, 60)
        LGRAY = (210, 210, 209)
        BLACK = (0, 0, 0)
        
        #draw tracks, slides and slide outlines for tileSet
        pygame.draw.rect(self.tileSetView, WHITE, self.trackX1, 0)
        pygame.draw.rect(self.tileSetView, WHITE, self.trackY1, 0)
        pygame.draw.rect(self.tileSetView, GRAY, self.slideX1, 0)
        pygame.draw.rect(self.tileSetView, GRAY, self.slideY1, 0)
        pygame.draw.rect(self.tileSetView, DGRAY, self.slideX1, 2)
        pygame.draw.rect(self.tileSetView, DGRAY, self.slideY1, 2)
        
        #draw tracks, slides and slide outlines for tileMap
        pygame.draw.rect(self.tileMapView, WHITE, self.trackX2, 0)
        pygame.draw.rect(self.tileMapView, WHITE, self.trackY2, 0)
        pygame.draw.rect(self.tileMapView, GRAY, self.slideX2, 0)
        pygame.draw.rect(self.tileMapView, GRAY, self.slideY2, 0)
        pygame.draw.rect(self.tileMapView, DGRAY, self.slideX2, 1)
        pygame.draw.rect(self.tileMapView, DGRAY, self.slideY2, 1)
        
        #draw menu bar
        pygame.draw.rect(self.screen, LGRAY, self.menuRect, 0)
        pygame.draw.line(self.screen, BLACK, 
                         (0, self.menuRect.height), 
                         (self.menuRect.width, self.menuRect.height), 3)
        
        #draw save button
        if self.saveActive:
            pygame.draw.rect(self.screen, SAVEIN, self.saveButton, 0)
            pygame.draw.rect(self.screen, SAVE, (16, 16, 96, 64), 3)
            font=pygame.font.Font(None, 35)
            text=font.render("Save", 1, SAVE)
            self.screen.blit(text, (self.saveButton.right/3 - 1, self.saveButton.bottom/2 - 3))
        else:
            pygame.draw.rect(self.screen, SAVE, self.saveButton, 0)
            pygame.draw.rect(self.screen, BLACK, (16, 16, 96, 64), 3)
            font=pygame.font.Font(None, 35)
            text=font.render("Save", 1, BLACK)
            self.screen.blit(text, (self.saveButton.right/3 - 1, self.saveButton.bottom/2 - 3))
    
    #to be completed later...
    def saveTileMap(self):
        #get image of entire tileMap
        iMin = 0
        iMax = len(self.tileMapArr)
        jMin = 0
        jMax = len(self.tileMapArr)
            
        #draw tile images to refresh surface and blit
        saveArray = []
        for i in range(iMin, iMax):
            col = []
            saveArray.append(col)
            for j in range(jMin, jMax):
                tile = self.tileMapArr[i][j]
                col.append(tile.getIndex())
    
        saveName = "tileMapSave.json"
        with open(saveName, 'wb') as outfile:
                    json.dump(saveArray, outfile)     
                    
    #loads tile table into memory
    def loadTileSetImage(self, tileSize, filename):
        if os.path.isfile(filename):   
            image = pygame.image.load(filename).convert_alpha()   #import tile table image
            table_width, table_height = image.get_size() #get tileSize & height of picture
            tile_table = [] #create array to hold individual tiles
            for x in range(0, table_width/tileSize): #go through windowX1 tiles
                col = [] #create columns..
                tile_table.append(col) #..and append to array 
                for y in range(0, table_height/tileSize): #go through windowY1 tiles
                    region = (x * tileSize, y * tileSize, tileSize, tileSize)
                    idx = table_width/tileSize * y + x
                    tile = Tile(image.subsurface(region), idx, tileSize, x, y)
                    col.append(tile) #subsurface references parent image
            return tile_table
#         else:   #return dummy array, for now
#             img = PIL.Image.new("RGBA", (tileSize, tileSize))
#             tileSurf = pygame.image.fromstring(img.tostring(), img.size, img.mode)
#             defaultTile = Tile(tileSurf, None, tileSize, 0, 0)
#             transparentTileArr = [defaultTile] * 10
#             transparentTileArr = []
#             for i in range(32):
#                 transparentTileArr.append([defaultTile] * 32)
#             return transparentTileArr
                 
    #sets window position variables in multiples of 32
    def setWindow1Pos(self, x, y):
        self.windowX1 = x
        self.windowY1 = y
        self.windowTileX1 = math.trunc(x / self.tileSize) * self.tileSize
        self.windowTileY1 = math.trunc(y / self.tileSize) * self.tileSize
        
    #sets window position variables in multiples of 32
    def setWindow2Pos(self, x, y):
        self.windowX2 = x
        self.windowY2 = y
        self.windowTileX2 = math.trunc(x / self.tileSize) * self.tileSize
        self.windowTileY2 = math.trunc(y / self.tileSize) * self.tileSize
             
    def scrollX1Update(self, event):
        if event.rel[0] != 0:
            moveX = max(event.rel[0], self.trackX1.left - self.slideX1.left)
            moveX = min(moveX, self.trackX1.right - self.slideX1.right - self.scrollThickness)#0,15,20,22,24,25,26,26
            if moveX != 0:
                self.slideX1.move_ip((moveX, 0))
    
    def getScrollX1State(self):
        if self.scrollingX1 == False:
            return False
        else:
            return True
    
    def setScrollX1State(self, state):
        self.scrollingX1 = state
    
    #returns true if cursor is inside of horizontal tileSet slider    
    def checkSlideX1Event(self, event):
        return self.slideX1.collidepoint(event.pos)
    
    def scrollY1Update(self, event):
        if event.rel[1] != 0:
            moveY = max(event.rel[1], self.trackY1.top - self.slideY1.top)
            moveY = min(moveY, self.trackY1.bottom - self.slideY1.bottom - self.scrollThickness)
            if moveY != 0:
                self.slideY1.move_ip((0, moveY))
            
    def getScrollY1State(self):
        if self.scrollingY1 == False:
            return False
        else:
            return True
        
    def setScrollY1State(self, state):
        self.scrollingY1 = state
    
    #returns true if cursor is inside of vertical tileSet slider
    def checkSlideY1Event(self, event):
        return self.slideY1.collidepoint(event.pos) 
    
    def scrollX2Update(self, event):
        if event.rel[0] != 0:
            moveX = max(event.rel[0], self.trackX2.left - self.slideX2.left)
            moveX = min(moveX, self.trackX2.right - self.slideX2.right - self.scrollThickness)#0,15,20,22,24,25,26,26
            if moveX != 0:
                self.slideX2.move_ip((moveX, 0))
    
    def getScrollX2State(self):
        if self.scrollingX2 == False:
            return False
        else:
            return True
    
    def setScrollX2State(self, state):
        self.scrollingX2 = state
       
    #returns true if cursor is inside of horizontal tileMap slider    
    def checkSlideX2Event(self, event):
        x, y = event.pos
        x -= self.tileSetViewRect.width
        return self.slideX2.collidepoint(x, y)
    
    def scrollY2Update(self, event):
        if event.rel[1] != 0:
            moveY = max(event.rel[1], self.trackY2.top - self.slideY2.top)
            moveY = min(moveY, self.trackY2.bottom - self.slideY2.bottom - self.scrollThickness)
            if moveY != 0:
                self.slideY2.move_ip((0, moveY))
            
    def getScrollY2State(self):
        if self.scrollingY2 == False:
            return False
        else:
            return True
        
    def setScrollY2State(self, state):
        self.scrollingY2 = state   
    
    #returns true if cursor is inside of vertical tileMap slider    
    def checkSlideY2Event(self, event):
        x, y = event.pos
        x -= self.tileSetViewRect.width
        return self.slideY2.collidepoint(x, y) 
    
    def setClickPos(self, curser):
        x, y = curser
        self.clickX = x
        self.clickY = y

    def canDraw(self):
        relClickX = self.clickX + self.windowX1  #relative clicks to current window position
        relClickY = self.clickY + self.windowY1
        tileX = math.trunc(relClickX / self.tileSize) * self.tileSize   #convert to the nearest upper left portion of tile in grid
        tileY = math.trunc(relClickY / self.tileSize) * self.tileSize
        #print self.drewTileX,",",tileX,"::",self.drewTileY,",",tileY
        if self.drewTileX == tileX and self.drewTileY == tileY:
            return False
        else:
            return True

    def checkForSaveHover(self, event):
        return self.saveButton.collidepoint(self.clickX, self.clickY)
    
    def getSaveActive(self):
        return self.saveActive 
    
    def setSaveActive(self, value):
        self.saveActive = value


class Controller:
    def __init__ (self, mdl):
        self.state = True   #used to see if anything in model was changed due to Controller
        self.drag = False   #used to determine if a click and drag is being established
        Controller.model = mdl
        # Map the back button to the escape key.
        if android:
            android.init()
            android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
            
    def update(self, event, running):
        self.state = True
        Controller.model.setClickPos(pygame.mouse.get_pos())    #update curser coordinates for model
        Controller.model.checkForSaveHover(event)
        #exit game if close button is pressed
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running[0] = False
            self.state = False
            #print 0
        elif (event.type == pygame.MOUSEMOTION and Controller.model.getScrollX1State()):
            Controller.model.scrollX1Update(event)
        elif (event.type == pygame.MOUSEMOTION and Controller.model.getScrollX2State()):
            Controller.model.scrollX2Update(event)
            #print 1
        elif (event.type == pygame.MOUSEMOTION and Controller.model.getScrollY1State()):
            Controller.model.scrollY1Update(event)
        elif (event.type == pygame.MOUSEMOTION and Controller.model.getScrollY2State()):
            Controller.model.scrollY2Update(event)
            #print 2
        elif event.type == pygame.MOUSEBUTTONDOWN and Controller.model.checkSlideX1Event(event):
            Controller.model.setScrollX1State(True)
        elif event.type == pygame.MOUSEBUTTONDOWN and Controller.model.checkSlideX2Event(event):
            Controller.model.setScrollX2State(True)
            #print 3
        elif event.type == pygame.MOUSEBUTTONDOWN and Controller.model.checkSlideY1Event(event):
            Controller.model.setScrollY1State(True)
        elif event.type == pygame.MOUSEBUTTONDOWN and Controller.model.checkSlideY2Event(event):
            Controller.model.setScrollY2State(True)
            #print 4
        elif event.type == pygame.MOUSEBUTTONDOWN and Controller.model.checkForSaveHover(event):
            Controller.model.setSaveActive(True)
        elif event.type == pygame.MOUSEBUTTONUP and Controller.model.getSaveActive():
            Controller.model.setSaveActive(False)
        elif event.type == pygame.MOUSEBUTTONUP:
            Controller.model.setScrollX1State(False)
            Controller.model.setScrollY1State(False)
            Controller.model.setScrollX2State(False)
            Controller.model.setScrollY2State(False)
            self.drag = False
            self.state = False
            #print 5
        #detect click and drag and send to module to set tile
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.drag = True
            Controller.model.setClickPos(pygame.mouse.get_pos())
            #print 6
        elif (self.drag and event.type == pygame.MOUSEMOTION and
              Controller.model.canDraw()):
            Controller.model.setClickPos(pygame.mouse.get_pos())
            #print 7
        #turn off flag for holding down mouse button
        else:
            self.state = False
            #print 8
            
    def doUpdate(self):
        return self.state      
 
 
            
class View():
    def __init__ (self):
        self.screen = pygame.display.set_mode((1024, 768))   #768, 1024 tablet size
        self.fps = 60    # The FPS the game runs at.
        self.clock = pygame.time.Clock()
        View.model = Model(self.screen, 64, 64, 32)
        View.controller = Controller(View.model)
        #---------------------------       
        View.model.update()
        pygame.display.update()
        self.clock.tick(self.fps)
        pygame.display.set_caption("fps: " + str(self.clock.get_fps()))
    
    #contains game spinner  
    def run(self): 
        running = [True]
        while running[0]:
            event = pygame.event.wait()
            # Android-specific:
            if android:
                if android.check_pause():
                    android.wait_for_resume()
            #Update controller
            View.controller.update(event, running)
            #Update model
            if View.controller.doUpdate():  #only update screen and module if a userevent occurs in controller
                View.model.update()
                pygame.display.update()
            #View FPS
            self.clock.tick(self.fps)
            pygame.display.set_caption("fps: " + str(self.clock.get_fps()))
     
     
            
def main():
    pygame.init()
    view = View()
    view.run()

# This isn't run on Android.
if __name__ == "__main__":
    main()