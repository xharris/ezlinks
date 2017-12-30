'''

READ FIRST:

	before running this script:
	1. open Duel Links
	2. press Initiate Link
	3. go through any opening dialogs or news dialogs

	so far this is WINDOWS ONLY since:
	- WinController.refreshWindowRect() uses ctypes 

'''

import os
from ezlinks import DuelLinks, WinController


duel_links = DuelLinks()
duel_links.duelNPC()
