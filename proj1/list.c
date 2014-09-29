#include "item.h"
#include "list.h"
#include <stdlib.h>

struct list{
	Item item;
	struct list *next;
};

/* initialises a list. returns pointer to that list */
list *LSTinit()
{
	return NULL;
}

/* creates new element in list. returns pointer to new in list. NULL on memory allocation error */
list *LSTadd(list *next, Item item)
{
	list *new;
	new = malloc(sizeof(list));
	if(new==NULL)
		return NULL;
	new->item = item;
	new->next = next;
	return new;
}

/* removes to_remove from list. returns pointer to the element in list after to_remove. prev is edited so that it points to the element in list following to_remove. if to_remove is NULL, prev element will point to NULL and NULL is returned.if prev == NULL it means you want to remove the first element of the list.*/
list *LSTremove(list *prev, list *to_remove, void(*free_item)(Item))
{
	list *aux;

	if(to_remove==NULL)
	{
		if(prev!=NULL)
			prev->next = NULL;
		aux = NULL;
	}
	else
	{
		aux = to_remove->next;
		(*free_item)(to_remove->item);
		free(to_remove);
		if(prev!=NULL)
			prev->next = aux;
	}

	return aux;
}

/* destroys the list pointed to by lst. uses the function free_item to dealocate the memory of each item in the list */
void LSTdestroy(list *lst, void (*free_item)(Item))
{
	while(lst!=NULL)
	{
		lst = LSTremove(NULL, lst, free_item);
	}
}

/* edits current so that the following on list will be pointed to by following. returns following */
list *LSTeditfollowing(list *current, list *following)
{
	if(current!=NULL)
		current->next = following;
	return following;
}

/* returns a pointer to the item stored in element of the list pointed to by element. returns NULL if element is NULL */
Item LSTgetitem(list *element)
{
	if(element!=NULL)
		return element->item;
	return NULL;
}

/* returns the address of the element that follows current in the list. if current is NULL, NULL is returned */
list *LSTfollowing(list *current)
{
	if(current!=NULL)
		return current->next;
	return NULL;
}

/* applies the function pointed to by function to the item inside element. item can be used to pass information to function. returns the return value of function, which should then be properly cast to the return type of function */
Item LSTapply(list *element, Item (*function)(Item, Item), Item item)
{
	return (*function)(element->item, item);
}



/*

EXAMPLES

list: a->b->c->d-> ... j->k->l-> ... ->z

--
adding an element in the middle of an existing list:

k = LSTeditfollowing(j, LSTadd(LSTfollowing(j), item));

--
destroying a list from a certain element onwards:

LSTdestroy(&k, void (*free_item)(Item));
LSTeditfollowing(j, NULL);

*/
