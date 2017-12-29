from ezlinks import WinController, ImageLocator
import match

'''
game_window = WinController(r"world")
if game_window.isReady():
	game_window.bringToFront()
'''

img_finder = ImageLocator()
img_finder.locate('douche1.png')


match.match('C:/Users/Gene/Desktop/ezlinks/src/images/douche1.png', 'C:/Users/Gene/Desktop/ezlinks/src/images/world.png')