#include <stdio.h>
#include <stdlib.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <unistd.h>

#define SHM_KEY 123456

int *ptr;

int main () {
    int id;

    /************************* TODO 1 *************************/
    // Create a shared memory section
	/*
		shmget notes
		shmget(key_t key, size_t size, int shmflg);
			size: assign the shared memory size
			shmflg:
				0666: authority
				IPC_CREAT: create a shared memory, if it already existed then open it.
	*/
	int shmid = shmget(SHM_KEY, 1, 0666|IPC_CREAT);
    /************************* TODO 1 *************************/

    /************************* TODO 2 *************************/
    // Attach the memory section
    // the return value is a pointer to the shared memory section
    /*
		shmat notes
		shmat(int shmid, const void *shmaddr, int shmflg);
			shmid: use which shared memory id
			shmaddr: assign the position where shared memery point,
					assign NULL let os determine.
	*/
	ptr = (int*) shmat(shmid, NULL, 0);
	/************************* TODO 2 *************************/

    ptr[0] = 0;
    printf("\033[1;32m[server] The value is %d\033[0m\n", ptr[0]);

    while(1) {
        int cmd;

        printf("\n");
        printf("1: Show the value\n");
        printf("2: Modify the value\n");
        printf("3: Exit\n");
        printf("Enter commands: ");
        scanf("%d", &cmd);

        if (cmd == 1)
            printf("\033[1;32m[server] The value is %d\033[0m\n", ptr[0]);
        else if (cmd == 2) {
            printf("Input new value: ");
            scanf("%d", &ptr[0]);
        }
        else
            break;        
    } 
}
