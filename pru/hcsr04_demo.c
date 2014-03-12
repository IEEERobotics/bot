// Standard includes
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

// PRUSS interface library
#include <prussdrv.h>
#include <pruss_intc_mapping.h>

#include <unistd.h>

void cleanup(int sig) {
    printf("\n");
    printf("Received signal %d, disabling PRU... ", sig);
    prussdrv_pru_disable (0);
    prussdrv_exit ();
    printf("done!\n");
    exit(0);
}


int main (void)
{

    signal(SIGINT, cleanup);
    signal(SIGTERM, cleanup);

    /* Initialize the PRU */
    printf("Initializing PRU\n");
    tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_INITDATA;
    prussdrv_init ();

    /* Open PRU Interrupt */
    if(prussdrv_open(PRU_EVTOUT_0))
    {
        // Handle failure
        fprintf(stderr, "prussdrv_open open failed\n");
        return 1;
    }

    /* Get the interrupt initialized */
    prussdrv_pruintc_init(&pruss_intc_initdata);

    /* Get pointers to PRU local memory */
    void *pruDataMem;
    prussdrv_map_prumem (PRUSS0_PRU0_DATARAM, &pruDataMem);
    unsigned int *pruData = (unsigned int *) pruDataMem;
    //flush?

    /* Execute example on PRU */
    printf("Executing sonar pru code\n");
    prussdrv_exec_program (0, "ultrasonic.bin");

    int count = 0;
    int us_addr = 0;
    int pulse_time = 0;
    while(1)
    {
        // Wait for the PRU interrupt to occur
        prussdrv_pru_wait_event (PRU_EVTOUT_0);
        prussdrv_pru_clear_event (PRU_EVTOUT_0, PRU0_ARM_INTERRUPT);
        // still something fishy in the interrupt handling, causing duplicate
        // interrupts... so (sleep and) reread =(
        // There's a 33ms delay in the ultrasonic logic, so the extra delay
        // should be harmless
        //usleep(1);
        prussdrv_pru_wait_event (PRU_EVTOUT_0);
        prussdrv_pru_clear_event (PRU_EVTOUT_0, PRU0_ARM_INTERRUPT);

        // Print out the distance received from the sonar (sound takes 58.77
        // microseconds to travel 1 cm at sea level in dry air)
        printf("%04d :\n", count);
        for(int pru = 0; pru < 4; pru++) {
            us_addr = pru * 2;
            printf("       Pre-pulse (count) = %d\n", (int) pruData[us_addr+1]);
            pulse_time = pruData[us_addr];
            printf("       Pulse (us) = %d\n", (int) pulse_time);
            printf("       Distance = %0.2f cm\n", (float) pulse_time / 58.77);
            printf("       Distance = %0.2f in\n", (float) pulse_time / 149.3);
            printf("\n");
        }
        count++;
    }

    return(0);

}
