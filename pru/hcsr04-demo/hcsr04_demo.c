// Standard includes
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

// PRUSS interface library
#include <prussdrv.h>
#include <pruss_intc_mapping.h>

#include <unistd.h>

void cleanup(int sig) {
    printf("Disabling PRU\n");
    prussdrv_pru_disable (0);
    prussdrv_exit ();
    printf("Done\n");
    exit(0);
}


int main (void)
{

    signal(SIGINT, cleanup);

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
    prussdrv_exec_program (0, "hcsr04_demo.bin");

    int i = 0;
    while(1)
    {
        // Wait for the PRU interrupt to occur
        prussdrv_pru_wait_event (PRU_EVTOUT_0);
        //prussdrv_pru_clear_event (PRU0_ARM_INTERRUPT, PRU_EVTOUT_0);
        prussdrv_pru_clear_event (PRU_EVTOUT_0, PRU0_ARM_INTERRUPT);
        // still something fishy in the interrupt handling causing 
        // duplicate interrupts... so sleep and reread =(
        // There's a 33ms delay in the ultrasonic logic, so it should be harmless
        //usleep(1);
        prussdrv_pru_wait_event (PRU_EVTOUT_0);
        prussdrv_pru_clear_event (PRU_EVTOUT_0, PRU0_ARM_INTERRUPT);

        // Print out the distance received from the sonar (sound takes 58.77 microseconds to travel 1 cm at sea level in dry air)
        printf("%04d :\n", i);
        printf("       Pre-pulse (count) = %d\n", (int) pruData[1]);
        printf("       Pulse (us) = %d\n", (int) pruData[0]);
        //printf("      Flag = %d\n", (int) pruData[2]);
        printf("       Distance = %f cm\n", (float) pruData[0] / 58.77);
        printf("       Distance = %f in\n", (float) pruData[0] / 149.3);
        printf("\n");
        printf("       Pre-pulse (count) = %d\n", (int) pruData[3]);
        printf("       Pulse (us) = %d\n", (int) pruData[2]);
        //printf("      Flag = %d\n", (int) pruData[2]);
        printf("       Distance = %f cm\n", (float) pruData[2] / 58.77);
        printf("       Distance = %f in\n", (float) pruData[2] / 149.3);
        i++;
    }

    return(0);

}
