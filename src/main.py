'''

EZ Links - duel links 'assistance' tool hehe xd
started: 12/28/17

DEVELOPMENT:

	- see requirements.txt for required python libraries

RUNNING:

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
