import win32api, win32gui, win32con, re, time, pyautogui, os, cv2
import numpy
from vk_code import VK_CODE

class WinController():
	def __init__(self, program_name):
		# check if window is open
		target_title = ''
		win_titles = enum_window_titles()
		print("Window search results:")
		for w in win_titles:
			if w.strip() not in ['', 'Default IME', 'MSCTFIME UI', 'G'] and re.search(program_name, w.strip()):
				print('\t'+w.strip())
				target_title = w
		
		# get info about the window
		self.win_title = target_title
		self.hwnd = win32gui.FindWindow(None, target_title)
		print("hwnd: "+str(self.hwnd))

		# found a valid window?
		if self.hwnd == 0:
			self.is_ready = False
			print("Window could not be controlled...")
		else:
			self.is_ready = True
			self.refreshWindowRect()
			print("window rect: x={} y={} w={} h={}".format(*self.win_rect))

	def isReady(self):
		return self.is_ready

	# set window left/top to (0,0)
	# still a little off
	def zeroPosition(self):
		win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0, 0, self.win_rect[2], self.win_rect[3], 0)

	def bringToFront(self):
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
		pyautogui.moveTo(x,y)
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
		self.win_rect = win32gui.GetClientRect(self.hwnd)


# get a list of open processes
def enum_window_titles():
    def callback(handle, data):
        titles.append(win32gui.GetWindowText(handle))

    titles = []
    win32gui.EnumWindows(callback, None)
    return titles

class ImageLocator():
	image_folder = os.path.join(os.getcwd(), 'src', 'images') 	# folder containing images used for locating regions on screen
	
	def __init__(self):
		self.screenshots = ['world.png']

	def takeScreenshot(self):
		pass

	def clearScreenshots(self):
		# delete each one

		# reset array
		pass

	# locate the position on an image using screenshots
	def locate(self, template):
		for main_image in self.screenshots:
			# prepare large image
			img_haystack = cv2.imread(os.path.join(self.image_folder, main_image))
			img_haystack_gray = cv2.cvtColor(img_haystack, cv2.COLOR_BGR2GRAY)

			# prepare image being searched for
			img_needle = cv2.imread(os.path.join(self.image_folder, template), 0)
			needle_w, needle_h = img_needle.shape[::-1]

			# do some hand waving
			print("finding "+template+" in "+main_image)
			res = cv2.matchTemplate(img_haystack_gray, img_needle, cv2.TM_CCOEFF_NORMED)
			threshold = 0.8
			loc = numpy.where(res >= threshold)

			# draw a rectangle where it was found
			for point in zip(*loc[::-1]):
				print("\tfound at ("+str(point[0])+", "+str(point[1])+")")
				cv2.rectangle(img_haystack, point, (point[0] + needle_w, point[1] + needle_h), (0,0,255), 2)
			cv2.imwrite(os.path.join(self.image_folder, main_image), img_haystack)
			