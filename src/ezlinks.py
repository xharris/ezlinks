import win32api, win32gui, win32con, re, time, pyautogui, os, cv2, imutils
import numpy
import mss, mss.tools
from vk_code import VK_CODE

import ctypes.wintypes
from ctypes import wintypes, windll, sizeof, byref

# check if we're in the src folder or in the root folder
_src = os.path.join(os.getcwd(),'src') if 'src' not in os.getcwd() else os.path.join(os.getcwd())

class WinController():
	screenshot_folder = os.path.join(_src, 'screenshots')

	def __init__(self, program_name):
		target_title = ''
		win_titles = enum_window_titles()
		print("Window search results:")

		results = 0
		for w in win_titles:
			if w.strip() not in ['', 'Default IME', 'MSCTFIME UI', 'G'] and re.search(program_name, w.strip()):
				print('\t'+w.strip())
				target_title = w
				results += 1

		#could not find the window
		if results == 0:
			raise Exception(program_name+" could not be found...")

		# valid window found
		else:
			# get info about the window
			self.win_title = target_title
			self.hwnd = win32gui.FindWindow(None, target_title)
			print("hwnd: "+str(self.hwnd))

			self.refreshWindowRect()

	# set window left/top to (0,0)
	# still a little off
	def zeroPosition(self):
		win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0, 0, self.win_rect[2], self.win_rect[3], 0)

	def bringToFront(self):
		win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
		win32gui.BringWindowToTop(self.hwnd)
		win32gui.SetForegroundWindow(self.hwnd)

	# types text in currently focused element
	def sendText(self, value):
		for k in value:
			win32api.keybd_event(VK_CODE[k], 0,0,0)
			win32api.keybd_event(VK_CODE[k], 0, win32con.KEYEVENTF_KEYUP, 0)

	def sendTextToPosition(self, x, y, value):
		pass

	def click(self, x, y):
		self.refreshWindowRect()
		x += self.win_rect[0]
		y += self.win_rect[1]

		self.bringToFront()
		pyautogui.click(x,y)
		''' # sending click to background window doesn't work
		lParam = (y << 16) | x # position to click
		print(win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 0, lParam))
		print(win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lParam))
		'''

	def getMouseXY(self):
		return win32api.GetCursorPos()

	def getRelMouseXY(self):
		x, y = self.getMouseXY()
		self.refreshWindowRect()
		return x - self.win_rect[0], y - self.win_rect[1]

	def refreshWindowRect(self):
		foundwindow = ctypes.windll.dwmapi.DwmGetWindowAttribute
		rect = ctypes.wintypes.RECT()
		DWMWA_EXTENDED_FRAME_BOUNDS = 9
		foundwindow(
			ctypes.wintypes.HWND(self.hwnd),
			ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
			ctypes.byref(rect), ctypes.sizeof(rect)
		)
		x, y, w, h = (rect.left, rect.top, rect.right-rect.left, rect.bottom-rect.top)
		self.win_rect = [x, y, w, h]
		print("window rect: x={} y={} w={} h={}".format(*self.win_rect))

	def takeScreenshot(self, save_name):
		self.refreshWindowRect()
		self.bringToFront()
		
		# create screenshot dir
		if not os.path.exists(os.path.join(_src,'screenshots')):
			os.makedirs(os.path.join(_src,'screenshots'))

		# take a screenshot
		screenshot_path = os.path.join(_src,'screenshots',save_name+'.png')
		with mss.mss() as sct:
			shot = sct.grab({
				'left':self.win_rect[0], 'top':self.win_rect[1],
				'width':self.win_rect[2], 'height':self.win_rect[3]
			})
			mss.tools.to_png(shot.rgb, shot.size, screenshot_path)
		print("wrote screenshot: "+screenshot_path)
		return screenshot_path

# get a list of open processes
def enum_window_titles():
	def callback(handle, data):
		titles.append(win32gui.GetWindowText(handle))

	titles = []
	win32gui.EnumWindows(callback, None)
	return titles

class ImageLocator():
	image_folder = os.path.join(_src, 'images')

	def __init__(self):
		# images used for locating regions on screen
		self.image_source = ''
		self.res = None

	def setImageSource(self, src):
		self.image_source = src
		if not os.path.isfile(self.image_source):
			raise Exception("image not found: "+self.image_source)

	# returns C:/Documents/whatever/<png_name>.png
	def createImagePath(self, png_name):
		return os.path.join(self.image_folder, png_name+'.png')

	'''
	locate the position on an image in a larger one
	returns a list of dicts with the structure: {src, x, y, w, h}
		- src: image source where the template was found
		- x, y, w, h: location rectangle	
	partly from https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
	'''
	def locate(self, img_template):
		if self.image_source != '' and os.path.isfile(img_template):
			template = cv2.imread(img_template) # loads image
			template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) # convert to grayscale
			template = cv2.Canny(template, 50, 200) # detects edges???
			(tH, tW) = template.shape[:2]

			# idk if this will work for our circular images but we'll try
			image = cv2.imread(os.path.join(self.image_folder,self.image_source))
			image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			found = None

			for scale in numpy.linspace(0.2, 1.0, 20)[::-1]:
				resized = imutils.resize(image, width = int(image.shape[1] * scale))
				r = image.shape[1] / float(resized.shape[1])

				if resized.shape[0] < tH or resized.shape[1] < tW:
					break

				edged = cv2.Canny(resized, 50, 200)
				result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
				(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

				# draw a bounding box around the detected region
				#clone = numpy.dstack([edged, edged, edged])

				if found is None or maxVal > found[0]:
					found = (maxVal, maxLoc, r)

			(_, maxLoc, r) = found
			(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
			(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
			
			return [startX,startY,endX-startX,endY-startY]
		return None

	def createResultImage(self):
		if self.image_source != '':
			from shutil import copyfile
			copyfile(self.image_source, os.path.join(_src, "screenshots", "result.png"))

	def drawResultRect(self, x, y, w, h):
		if self.image_source != '':
			result_img = cv2.imread(os.path.join(_src, "screenshots", "result.png"))
			cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 0, 255), 2)
			cv2.imwrite(os.path.join(_src, "screenshots", "result.png"), result_img)

	# binary search to find an optimal threshold
	def findThreshold(self, res):
		if self.res is not res:
			self.res = res

		return self._findThreshold()

	def midpoint(self, lower_bound, upper_bound):
		return (lower_bound + upper_bound) / 2

	def _findThreshold(self, lower_bound=0, upper_bound=1.0, iters=0):
		print("ITER[{}], LOWER[{}], UPPER[{}]".format(iters, lower_bound, upper_bound))
		if self.res is None:
			print("Could not find threshold: res was null")
			return

		threshold = self.midpoint(lower_bound, upper_bound)

		# 1000 is failsafe
		if iters > 100 or lower_bound == upper_bound:
			print("Could not find threshold: failsafe condition was met")
			return threshold

		# only need to compute for one dimension since it's impossible for a point to exist with an x and not a y
		if len(numpy.where(self.res >= threshold)[0]) == 0:
			#not found, lowering threshold
			print("NOT FOUND")
			return self._findThreshold(lower_bound, threshold, iters=iters+1)
		elif len(numpy.where(self.res >= threshold)[0]) > 1:
			#found! let's try increasing threshold
			print("FOUND")
			return self._findThreshold(threshold, upper_bound, iters=iters+1)
		else:
			# found exactly one instance, we're good!
			return threshold

class DuelLinks():
	NPC_NAMES = ["standard", "legend"]
	def __init__(self):
		self.img_locator = ImageLocator()
		self.win_ctrl = WinController("Yu-Gi-Oh! DUEL LINKS")
		self.npcs = []

		self.win_ctrl.bringToFront()

	# street: gate, pvp, shop, studio
	# TODO: add images to folder
	def goToStreet(self, street):
		img_path = os.path.join(self.img_locator.createImagePath(street))
		if os.path.isfile(img_path):
			self.npcs = []
		else:
			raise Exception("Street \'{}\' not found".format(street))

	# stores the coordinates of all found npcs
	def getAllNpc(self):
		img_world_path = self.win_ctrl.takeScreenshot("world")
		self.img_locator.setImageSource(img_world_path)
		self.img_locator.createResultImage()

		for name in self.NPC_NAMES:
			for i in range(0,3):
				npc_loc = self.img_locator.locate(self.img_locator.createImagePath(name+str(i)))
				if npc_loc != None and npc_loc[1] > self.win_ctrl.win_rect[3]/2:
					# offset from window position
					self.img_locator.drawResultRect(npc_loc[0], npc_loc[1], npc_loc[2], npc_loc[3])
					self.npcs.append(npc_loc)
					break # break first loop
		print("NPCs found:" +str(len(self.npcs))+"!")

	# duel any one npc found on the screen
	def duelNPC(self):
		self.getAllNpc()

		# offset from window position
		if len(self.npcs) > 0:
			npc = self.npcs.pop()
			self.win_ctrl.click(npc[0]+(npc[2]/2), npc[1]+(npc[3]/2))

	# check how many NPCs are in the world (excluding vagabonds and legendary duelists)
	def getPopulation():
		return 9 # hardcoded for now

	# autoduel until no one is left
	def cleanTheStreets(self):
		pass