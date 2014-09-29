#include "item.h"

#ifndef _LIST_H
#define _LIST_H

typedef struct list list;

list *LSTinit();
list *LSTadd(list *next, Item item);
list *LSTremove(list *prev, list *to_remove, void (*free_item)(Item));
void LSTdestroy(list *lst, void (*free_item)(Item));
list *LSTeditfollowing(list *current, list *following);
Item LSTgetitem(list *element);
list *LSTfollowing(list *current);
Item LSTapply(list *element, Item (*function)(Item, Item), Item item);

#endif
