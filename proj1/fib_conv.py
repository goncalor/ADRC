import random
import sys

newfileext = "_ed.txt"
nr_interfaces = 64

print "Usage: python " + sys.argv[0] + " <fib_files>"

for i in range(1, len(sys.argv)):
	filename = sys.argv[i]
	print filename
	read_file = open(filename, 'r')
	write_file = open(filename + newfileext, 'w')

	for line in read_file:
		prefix = ""
		split_slash = line.split('/')
		for i in range(4):
			prefix += "{0:b}".format(int(split_slash[0].split('.')[i])).zfill(8)

		write_file.write(prefix[:int(split_slash[1].split('\t')[0])] + "\t" + str(random.randrange(nr_interfaces)) + "\n")

	read_file.close()
	write_file.close()
