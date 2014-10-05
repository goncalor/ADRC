#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

#define ADDR_LEN	32	// address length in bits
#define LINE_LEN	ADDR_LEN + 6	// 1 whitespace char, max 3 interface digits, \n\0
#define DISCARD_VAL	-1	// interface value for discarded packets

#define DEBUG
#define DEBUGL2

typedef struct node{

	unsigned branchfact : 5;	// max branching factor 2^31
	unsigned skip : 7;	//	max skip is 127 (enough for IPv6)
	unsigned pointer : 20;	//	enough for 2^20 entries in the FIB. 516k on 23/9/1014

/*	unsigned char branchfact, skip;
	unsigned pointer;
*/} node;

typedef struct fib_entry{
	unsigned prefix;
	char prefixlen;
	short nexthop;
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

/* returns the skip value (longest common prefix in the interval) possible for the n entries in fib starting at index first. ignores the first pre bits. it is assumed all entries in the fib are different */
unsigned short compute_skip(fib_entry *fib, unsigned short pre, unsigned first, unsigned n)
{
	unsigned first_pre, last_pre;	// first and last prefixes in the interval
	short p;

	first_pre = fib[first].prefix;
	last_pre = fib[first+n-1].prefix;

	p = pre;
	while(extract(first_pre, p, 1) == extract(last_pre, p, 1))
		p++;

	return p - pre;
}

/* returns the branch value possible for the n entries in fib starting at index first. ignores the first pre bits. */
unsigned compute_branch(fib_entry *fib, unsigned short pre, unsigned first, unsigned n)
{
	short branch, m, found;
	unsigned i;

	if(n==2)
		return 1;

	branch=2;
	do
	{
		found = 0;
		for(m=0, i=0; i<n; i++)
			if(extract(fib[first + i].prefix, pre, branch) == m)
			{
				m++;
				if(m==(1<<branch))	// found all combinations for this branchfact
				{
					found = 1;
					branch++;
					break;
				}
			}
	}
	while(found);

	return --branch;
}


void build_trie(node *trie, fib_entry *fib, unsigned first, unsigned n, unsigned short pre, unsigned root_pos, unsigned *free_pos)
{
	unsigned short skip;
	unsigned first_child;	// position of first child for this node (local root)
	unsigned p, k, bitpat, branch;

	#ifdef DEBUGL2
	int i;
	for(i=0; i<n; i++)
		printf("%u\n", fib[first+i].prefix);
	puts("");
	#endif

	if(n == 1)
	{
		trie[root_pos].branchfact = trie[root_pos].skip = 0;
		trie[root_pos].pointer = first;
		return;
	}

	skip = compute_skip(fib, pre, first, n);
	branch = compute_branch(fib, pre + skip, first, n);

	first_child = *free_pos;
	trie[root_pos].branchfact = branch;
	trie[root_pos].skip = skip;
	trie[root_pos].pointer = first_child;

	*free_pos = first_child + (1<<branch);

	p = first;
	for(bitpat=0; bitpat<(1<<branch); bitpat++)
	{
		k=0;
		while(p+k < first+n && extract(fib[p + k].prefix, pre + skip, branch) == bitpat)
			k++;

		build_trie(trie, fib, p, k, pre + skip + branch, first_child + bitpat, free_pos);

		p += k;
	}
}


/* searches for address in trie and modifies nexthop to the value resulting from the search. returns nonzero on success. on failure nexthop is not affected */
int search_trie(node *trie, fib_entry *fib, unsigned address, short *nexthop)
{
	node node = trie[0];
	unsigned short skip = node.skip;
	unsigned branch = node.branchfact;
	unsigned addr = node.pointer;

	while(branch != 0)
	{
		node = trie[addr + extract(address, skip, branch)];
		skip = skip + branch + node.skip;
		branch = node.branchfact;
		addr = node.pointer;
	}

	if(extract(address ^ fib[addr].prefix, 0, fib[addr].prefixlen) == 0)	// found it
	{
		*nexthop = fib[addr].nexthop;
		return 1;
	}
	else
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
	short empty_nexthop=0;	// empty prefix interface

/* verify first line of file has empty prefix */

	fgets(line, LINE_LEN, fp);
	if(sscanf(line, "* %hd", &empty_nexthop) != 1)	// no next hop defined for empty prefix. choose a value to signal that packets should be discarded
	{
		empty_nexthop = DISCARD_VAL;
		printf("First line of '%s' is not the empty prefix. Some packets may be discarded.\n", argv[1]);
	}

/* load the FIB into memory */

	unsigned nrlines = 0;	// nr of lines in the FIB file
	fib_entry *fib;
	char prefix_str[ADDR_LEN+1];	// +1 for \0
	short nexthop = DISCARD_VAL, i;

	while(!feof(fp))
	{
		if(fgetc(fp) == '\n')
			nrlines++;
	}

	rewind(fp);
	if(empty_nexthop != DISCARD_VAL)	// BUG if empty nexthop is set to discard_val in the file
	{
		fgets(line, LINE_LEN, fp);	// skip the line with the empty prefix
	}
	else
		nrlines++;	// the first line had a prefix which we did not count

	#ifdef DEBUG
	printf("the FIB has %d entries (excluding empty prefix)\n", nrlines);
	#endif

	fib = malloc(nrlines*sizeof(fib_entry));
	memerr(fib);

	i = 0;
	while(fgets(line, LINE_LEN, fp) != NULL)
	{
		if(sscanf(line, "%[01] %hd", prefix_str, &nexthop) != 2)
		{
			printf("Malformed line in '%s'.\n\n", argv[1]);
			exit(0);
		}

		fib[i].prefix = binstrtoi_l(prefix_str);
		fib[i].prefixlen = strlen(prefix_str);
		fib[i].nexthop = nexthop;
		i++;
	}

	#ifdef DEBUG
	puts("\npref\t\tpreflen\tnexthop");
	for(i=0; i<10 && i < nrlines; i++)
		printf("%u\t%d\t%d\n", fib[i].prefix, fib[i].prefixlen, fib[i].nexthop);
	puts("...\n");
	#endif

/* sort the FIB by prefix */

	printf("Now sorting the FIB... ");
	qsort(fib, nrlines, sizeof(fib_entry), (cmpfn)fib_prefix_cmp);
	puts("Done.");

	#ifdef DEBUG
	puts("\npref\t\tpreflen\tnexthop");
	for(i=0; i<10 && i< nrlines; i++)
		printf("%u\t%d\t%d\n", fib[i].prefix, fib[i].prefixlen, fib[i].nexthop);
	puts("...\n");
	#endif

/* load data from the FIB and create a LC trie */

	#ifdef DEBUG
	printf("each node takes %ld Bytes to store\n\n", sizeof(node));
	#endif

	node *tmp_trie = malloc(100*sizeof(node));	//	!!
	unsigned free_pos = 1;	/* next free position in the trie. the trie root takes the first position */

	build_trie(tmp_trie, fib, 0, nrlines, 0, 0, &free_pos);

/* paste the trie into a vector with the correct size */

	node *trie = malloc(free_pos*sizeof(node));
	for(i=0; i<free_pos; i++)
		trie[i] = tmp_trie[i];
	free(tmp_trie);

	#ifdef DEBUG
	puts("i\tbranch\tskip\tpointer");
	for(i=0; i<free_pos; i++)
		printf("%d\t%d\t%d\t%d\t\n", i, trie[i].branchfact, trie[i].skip, trie[i].pointer);
	#endif

/* prompt for address and search trie */
	puts("To exit just press Enter.\n");

	char address[ADDR_LEN+1];	// +1 for \0

	printf("Address to look up: ");
	fgets(line, ADDR_LEN, stdin);

	while(sscanf(line, "%[01]", address)==1)
	{
		#ifdef DEBUG
		printf("search: %u\nreturn val: %d\n", binstrtoi_l(address), search_trie(trie, fib, binstrtoi_l(address), &nexthop));
		printf("nexthop: %d\n", nexthop);
		#endif

		if(search_trie(trie, fib, binstrtoi_l(address), &nexthop) != 0)	// found it
		{
			printf("Forward to interface %hd.\n", nexthop);
		}
		else
		{
			puts("Discard packet.");
		}

		printf("\nAddress to look up: ");
		fgets(line, ADDR_LEN, stdin);
	}


	puts("Bye.\n");

	free(trie);
	free(fib);
	fclose(fp);
	exit(0);
}
