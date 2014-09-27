#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

#define ADDR_LEN	32	// address length in bits
#define LINE_LEN	ADDR_LEN + 6	// 1 whitespace char, max 3 interface digits, \n\0
#define DISCARD_VAL	UINT_MAX	// interface value for discarded packets

#define DEBUG


typedef struct node{
	unsigned branchfact : 5;	// max branching factor 2^31
	unsigned skip : 7;	//	max skip is 127 (enough for IPv6)
	unsigned pointer : 20;	//	enough for 2^20 entries in the FIB. 516k on 23/9/1014
} node;

typedef struct fib_entry{
	unsigned prefix;
//	char prefixlen;
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

/* binary string to unsigned pushed left. example on 8 bits 101 -> 10100000 */
unsigned binstrtoi_l(char *str)
{
	short n;
	unsigned nr=0;

	for(n=0; str[n]!='\0' && n < sizeof(unsigned)*8; n++)
	{
		if(str[n]=='1')
			nr |= 1<<(sizeof(unsigned)*8-1-n);
	}
	return nr;
	/* return nr>>(sizeof(unsigned)*8-n);	for _r */
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


/* --------  -------- */

/* sets to 0 the n highest bits of nr */
unsigned clear_pre(unsigned nr, unsigned short n)
{
	return nr << n >> n;
}

/* extracts from nr the first n bits starting at position p (p=0 -> MSB) */
unsigned extract(unsigned nr, unsigned short p, unsigned short n)
{
	return nr << p >> (sizeof(unsigned)*8 - n);
}

/* returns the skip value possible for the n entries in fib starting at index first. ignores the first pre bits. it is assumed all entries in the fib are different */
unsigned short compute_skip(fib_entry *fib, unsigned short pre, unsigned first, unsigned n)
{
	unsigned first_pre, last_pre;	// first and last prefixes in the interval
	short p;

/*	first_cle = clear_pre(fib[first].prefix, pre);
	last_cle = clear_pre(fib[first+n-1].prefix, pre);*/

	first_pre = fib[first].prefix;
	last_pre = fib[first+n-1].prefix;

	p = pre;
	while(extract(first_pre, p, 1) == extract(last_pre, p, 1))
		p++;

	return p - pre;
}

/* returns the branch value possible for the n entries in fib starting at index first. ignores the first pre bits. */
unsigned short compute_branch(fib_entry *fib, unsigned short pre, unsigned first, unsigned n)
{
	short branch, m;
	unsigned i;

	if(n==2)
		return 1;

	for(branch=2, i=0; i<n; branch++)
	{
		for(i=0, m=0; m<((1<<branch)-1) && i<n; i++)
		{
			//printf("%d\t%d\t%d\n", branch, i, m);
			if(extract(fib[first + i].prefix, pre, branch) == m)
				m++;

		}
	}
	return branch-2;
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
	unsigned empty_nexthop=0;	// empty prefix interface

/* verify first line of file has empty prefix */

	fgets(line, LINE_LEN, fp);
	if(sscanf(line, "* %u", &empty_nexthop) != 1)	// no next hop defined for empty prefix. choose a value to signal that packets should be discarded
	{
		empty_nexthop = DISCARD_VAL;
		printf("First line of '%s' is not the empty prefix. Some packets may be discarded.\n", argv[1]);
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
	printf("the FIB has %d entries (excluding empty prefix)\n", nrlines);
	#endif

	fib = malloc(nrlines*sizeof(fib_entry));
	memerr(fib);

	rewind(fp);
	if(empty_nexthop != DISCARD_VAL)	// BUG if empty nexthop is set to discard_val in the file
	{
		fgets(line, LINE_LEN, fp);	// skip the line with the empty prefix
	}
	else
		nrlines++;	// the first line had a prefix which we did not count

	i = 0;
	while(fgets(line, LINE_LEN, fp) != NULL)
	{
		if(sscanf(line, "%[01] %u", prefix_str, &nexthop) != 2)
		{
			printf("Malformed line in '%s'\n\n", argv[1]);
			exit(0);
		}

		fib[i].prefix = binstrtoi_l(prefix_str);
//		fib[i].prefixlen = strlen(prefix_str);
		fib[i].nexthop = nexthop;
		i++;
	}

	#ifdef DEBUG
	puts("pref\t\tnexthop");
	for(i=0; i<10 && i < nrlines; i++)
		printf("%u\t%d\n", fib[i].prefix, fib[i].nexthop);
	puts("...");
	#endif

/* sort the FIB by prefix */

	qsort(fib, nrlines, sizeof(fib_entry), (cmpfn)fib_prefix_cmp);

	#ifdef DEBUG
	puts("pref\t\tnexthop");
	for(i=0; i<10 && i< nrlines; i++)
		printf("%u\t%d\n", fib[i].prefix, fib[i].nexthop);
	puts("...");
	#endif

/* load data from the FIB and create a LC trie */

	#ifdef DEBUG
	printf("each node takes %ld Bytes to store\n\n", sizeof(node));
	#endif


printf("%hu\n", compute_skip(fib, 0, 0, nrlines));

printf("%hu\n", compute_branch(fib, 0, 0, nrlines));










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
