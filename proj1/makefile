CC = gcc
CFLAGS = -Wall -g

all: 2trie compression LCtrie

# 2trie
2trie: 2trie.o
	$(CC) $(CFLAGS) $^ -o $@

2trie.o: 2trie.c
	$(CC) $(CFLAGS) -c $< -o $@

# compression
compression: ORTC.o list.o
	$(CC) $(CFLAGS) ORTC.o list.o -o compression

ORTC.o: ORTC.c
	$(CC) $(CFLAGS) -c ORTC.c

# LCtrie

LCtrie: LCtrie.o list.o
	$(CC) $(CFLAGS) $^ -o $@

LCtrie.o: LCtrie.c
	$(CC) $(CFLAGS) -c $< -o $@

# other
list.o: list.c list.h item.h
	$(CC) $(CFLAGS) -c list.c

c: 
	clear
	rm *.o



# $@ reffers to named before :
# $^ reffers to all named after :
# $< reffers to first after :
