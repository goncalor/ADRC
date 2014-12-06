import os
import sys
import glob
import filecmp

# set this to false if you want to generate new *.result files instead of testing
generate_new = False

files = list(set(glob.glob("graphs/*")) - set(glob.glob("graphs/*.png")) - set(glob.glob("graphs/*.exclude")))
prefix_lenght = len("graphs/")

for i, val in enumerate(files):
	files[i] = files[i][prefix_lenght:]

for filename in files:
	if not generate_new:
		os.system("python proj3.py graphs/" + filename + " --disable-prompt > results/" + filename + ".temp")
	
		if not filecmp.cmp("results/" + filename + ".result", "results/" + filename + ".temp"):
			print filename + " returned a different output"
		else:
			os.system("rm results/" + filename + ".temp")		
	
	else:
		os.system("python proj3.py graphs/" + filename + " --disable-prompt > results/" + filename + ".result")
		
