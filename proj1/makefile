compression: ORTC.o list.o
	gcc ORTC.o list.o -o compression

ORTC.o: ORTC.c
	gcc -c ORTC.c

list.o: list.c list.h item.h
	gcc -c list.c
