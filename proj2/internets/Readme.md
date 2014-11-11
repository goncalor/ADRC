#Internets

file | policy connected | short description  
:---------- | :---------- | :----------  
01.txt | yes | from page 1 of the assignment 
02.txt | yes |5 is a client to 3, 4 and 1. 3 and 4 are 2's clients. 2 is a client of 1
03.txt | no | 1 and 2 are peers. 2 and 3 are peers.
04.txt | no | unconnected graph, from page 2 of the assignment  
05.txt | yes | 5 is 4's client, who's 3's client, who's 2's client, who's 1's client
06.txt | yes | 2 and 3 are peers and are 1's clients
07.txt | no | 1 is a provider to 2. 2 is a peer to 3. 3 is a provider to 4.
08.txt | yes | 2, 3 and 4 are 1's clients. 3 is a peer of 2 and 4 but 2 and 4 are not peers. 2 has one client, 5
09.txt | no | 1 and 3 are policy disconnected and have common client, 2
10.txt | yes | 1 and 3 are peers and have a common client, 2
11.txt | yes | there is a cycle that might mislead the algorithm to pass twice by 2 when going from 1 to 5
