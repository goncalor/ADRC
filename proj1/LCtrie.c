#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define ADDR_LEN	32	// address length in bits
#define LINE_LEN	ADDR_LEN + 6	// 1 whitespace char, max 3 interface digits, \n\0

#define DEBUG


typedef struct node{
	unsigned branchfact : 5;	// max branching factor 2^31
	unsigned skip : 7;	//	max skip is 127 (enough for IPv6)
	unsigned pointer : 20;	//	enough for 2^20 entries in the FIB. 516k on 23/9/1014
} node;

typedef struct fib_entry{
	unsigned prefix;
	char prefixlen;
	unsigned nexthop;
} fib_entry;


void memerr(void *p)
{
	if(p==NULL)
	{
		puts("ERROR: Unable to allocate memory.");
		exit(-1);
	}
}

unsigned binstrtoi(char *str)
{
	short n;
	unsigned nr=0;

	for(n=0; str[n]!='\0' && n < sizeof(unsigned)*8; n++)
	{
		if(str[n]=='1')
			nr |= 1<<(sizeof(unsigned)*8-1-n);
	}
	return nr>>(sizeof(unsigned)*8-n);
}

typedef int (*cmpfn)(const void*, const void*);
int fib_prefix_cmp(fib_entry *a, fib_entry *b)
{
	if(a->prefix > b->prefix)
		return 1;
	if(a->prefix < b->prefix)
		return -1;
	return 0;
}

/* -------- MAIN -------- */

int main(int argc, char **argv)
{
	if(argc < 2)
	{
		printf("Usage: %s forwarding_table_file\n\n", argv[0]);
		exit(0);
	}

	FILE *fp = fopen(argv[1], "r");
	if(fp == NULL)
	{
		printf("Unable to open '%s'\n\n", argv[1]);
		exit(-1);
	}

	char line[LINE_LEN];
	unsigned empty_nexthop;	// empty prefix interface

/* verify first line of file has empty prefix */

	fgets(line, LINE_LEN, fp);
	if(sscanf(line, "* %u", &empty_nexthop) != 1)
	{
		printf("First line of '%s' is not the empty prefix.\n\n", argv[1]);
		exit(0);
	}

/* load the FIB into memory */

	unsigned nrlines = 0;	// nr of lines in the FIB file
	fib_entry *fib;
	char prefix_str[ADDR_LEN+1];	// +1 for \0
	unsigned prefix, nexthop, i;

	while(!feof(fp))
	{
		if(fgetc(fp) == '\n')
			nrlines++;
	}

	#ifdef DEBUG
	printf("the FIB has %d entries\n", nrlines);
	#endif

	fib = malloc(nrlines*sizeof(fib_entry));
	memerr(fib);

	rewind(fp);
	fgets(line, LINE_LEN, fp);	// skip the line with the empty prefix

	i = 0;
	while(fgets(line, LINE_LEN, fp) != NULL)
	{
		if(sscanf(line, "%[01] %u", prefix_str, &nexthop) != 2)
		{
			printf("Malformed line in '%s'\n\n", argv[1]);
			exit(0);
		}

		fib[i].prefix = binstrtoi(prefix_str);
		fib[i].prefixlen = strlen(prefix_str);
		fib[i].nexthop = nexthop;
		i++;
	}

	#ifdef DEBUG
	puts("pref\tlen\tnexthop");
	for(i=0; i<10 && i < nrlines; i++)
		printf("%d\t%d\t%d\n", fib[i].prefix, fib[i].prefixlen, fib[i].nexthop);
	puts("...");
	#endif

/* sort the FIB by prefix */

	qsort(fib, nrlines, sizeof(fib_entry), (cmpfn)fib_prefix_cmp);

	#ifdef DEBUG
	puts("pref\tlen\tnexthop");
	for(i=0; i<10 && i< nrlines; i++)
		printf("%d\t%d\t%d\n", fib[i].prefix, fib[i].prefixlen, fib[i].nexthop);
	puts("...");
	#endif

/* load data from the FIB and create a LC trie */

	#ifdef DEBUG
	printf("each node takes %ld Bytes to store\n\n", sizeof(node));
	#endif









/* prompt for address and search trie */
	puts("To exit just press Enter.\n");

	char address[ADDR_LEN+1];	// +1 for \0

	printf("Address to look up: ");
	fgets(line, LINE_LEN, stdin);

	while(sscanf(line, "%[01]", address)==1)
	{


	}






	puts("Bye.\n");


	fclose(fp);
	exit(0);
}
