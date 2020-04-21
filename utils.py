import sys
import os

def fix_path(filename):
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, filename)
	else:
		return filename