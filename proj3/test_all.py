import os
import sys
import glob
import filecmp

files = list(set(glob.glob("graphs/*")) - set(glob.glob("graphs/*.png")) - set(glob.glob("graphs/*.exclude")))
prefix_lenght = len("graphs/")

for i, val in enumerate(files):
	files[i] = files[i][prefix_lenght:]

for filename in files:
	os.system("python proj3.py graphs/" + filename + " --disable-prompt > results/" + filename + ".temp")
	
	if not filecmp.cmp("results/" + filename + ".result", "results/" + filename + ".temp"):
		print filename + " returned a different output"
	
	os.system("rm results/" + filename + ".temp")
		
