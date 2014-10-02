compression: ORTC.o list.o
	gcc -g -Wall ORTC.o list.o -o compression

ORTC.o: ORTC.c
	gcc -g -Wall -c ORTC.c

list.o: list.c list.h item.h
	gcc -g -Wall -c list.c

clean: 
	clear
	rm *.o
