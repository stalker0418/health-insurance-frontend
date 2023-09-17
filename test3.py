# from taipy import Config
# from functions import build_message




# name_data_node_cfg = Config.configure_data_node(id="name")
# message_data_node_cfg = Config.configure_data_node(id="message")
# build_msg_task_cfg = Config.configure_task("build_msg", build_message, name_data_node_cfg, message_data_node_cfg)
# scenario_cfg = Config.configure_scenario_from_tasks("scenario", task_configs=[build_msg_task_cfg])

# Config.export('my_config.toml')

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>

#define SHM_SIZE  sizeof(int)

// Function to increment the shared variable "total"
void process(int *total, int increment, int processNum) {
    while(*total <= increment) {
        (*total)++;
    }
    printf("From Process %d: counter = %d\n", processNum, *total);
}

int main() {
    int shmid;
    int *total;

    // Create shared memory segment
    shmid = shmget(IPC_PRIVATE, SHM_SIZE, IPC_CREAT | 0666);
    if (shmid == -1) {
        perror("shmget");
        return 1;
    }

    // Attach the shared memory segment
    total = (int *)shmat(shmid, NULL, 0);
    if (*total == -1) {
        perror("shmat");
        return 1;
    }

    // Initialize the shared variable "total" to 0
    *total = 0;

    // Create 4 child processes
    for (int i = 1; i <= 4; i++) {
        pid_t child_pid = fork();
        if (child_pid == 0) { // Child process
            if(i == 1) process(total, i * 1000000, i);
	    else if(i==2) process(total, i * 1000000, i);
	    else if(i==3) process(total, 4000000, i);
	    else if(i==4) process(total, 5000000, i);
		
            exit(0);
        } else if (child_pid < 0) {
            perror("fork");
            return 1;
        }
        else{
            wait(NULL)
        }
    }

    // Wait for all child processes to finish
    for (int i = 0; i < 4; i++) {
        int status;
        pid_t finished_pid = wait(&status);
        printf("Child with ID: %d has just exited.\n", finished_pid);
    }

    // Detach and remove the shared memory segment
    shmdt(total);
    shmctl(shmid, IPC_RMID, NULL);

    printf("End of Program.\n");

    return 0;
}