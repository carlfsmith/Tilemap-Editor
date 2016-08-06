# Tilemap-Editor
A visual editor which allows users to place tiles on a 2D map from an imported tileset.

The .android.json file is the configuration doc for the pygame subset for android(PS4A).

I've included the apk file for testing (if desired and possible) on an Android device.

I should warn you that the app runs painfully slow on Android(we're talking ~5 fps). I've experienced this on both my tablet and Bluestacks (an Android emulator that I'm using on Windows).

The version of Python used is 2.7, so if you're using the later version, there will at least be a regular fiesta of syntax errors. This version was needed in order to work with the latest version of PS4A (0.9.6). PS4A is available on both Windows and Linux systems

To insert your own tileset, you're going to need to go into the View class and adjust the Module constructor values in the initializer function to (image_name, desiredTilesWide, desiredTilesHigh, tileSize).

Resolution can be changed and everything but the menu should scale accordingly.

To end the program press the window close button or the escape key

To make the game fullscreen use pygame.FULLSCREEN as an additional argument for the display in the View initializer function
