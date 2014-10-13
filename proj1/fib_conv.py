import random

filename = "fibs/hbone/hbone_bme_2014_06_01_00_10_29.anon.txt"
newfileext = "_ed.txt"

read_file = open(filename, 'r')
write_file = open(filename + newfileext, 'w')

for line in read_file:
	#print line
	prefix = ""
	split_slash = line.split('/')
	for i in range(4):
		prefix += "{0:b}".format(int(split_slash[0].split('.')[i])).zfill(8)

	write_file.write(prefix[:int(split_slash[1].split('\t')[0])] + "\t" + str(random.randrange(64)) + "\n")


read_file.close()
write_file.close()

