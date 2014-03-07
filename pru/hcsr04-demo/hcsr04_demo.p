// Define the entry point of the program
.origin 0
.entrypoint START

// Base addresses of the low-level GPIO controllers
//  GPIO0: 0-31
//  GPIO1: 32-63, etc
#define GPIO0              0x44e07000
#define GPIO1              0x4804c000
#define GPIO2              0x481ac000
#define GPIO3              0x481ae000

// Offset for the control register of the gpio controller
#define GPIO_CTRL          0x130

// Offset for the output enable register of the gpio controller
#define GPIO_OE            0x134

// Offset for the data in register of the gpio controller
#define GPIO_DATAIN        0x138

// Offset for the data out register of the gpio controller
#define GPIO_DATAOUT       0x13c

// Offset for the clear data out register of the gpio controller
// Clears all pins where bit is 1 (rest unchanged)
#define GPIO_CLEARDATAOUT  0x190

// Offset for the set data out register of the gpio controller
// Sets all pins where bit is 1 (rest unchanged)
#define GPIO_SETDATAOUT    0x194

// PRU interrupt for PRU0
#define PRU0_ARM_INTERRUPT 19

// front (Trig: P9_25, Echo: P9_27)
#define TRIG1_CONT  GPIO3
#define TRIG1_GPIO  21
#define ECHO1_CONT  GPIO3
#define ECHO1_GPIO  19

// back (Trig: P8_11, Echo: P8_15)
#define TRIG2_CONT  GPIO1
#define TRIG2_GPIO  13
#define ECHO2_CONT  GPIO1
#define ECHO2_GPIO  15

// left (Trig: P9_30, Echo: P9_24)
#define TRIG3_CONT  GPIO3
#define TRIG3_GPIO  16
#define ECHO3_CONT  GPIO0
#define ECHO3_GPIO  15

// right (Trig: P9_29, Echo: P9_31)
#define TRIG4_CONT  GPIO1
#define TRIG4_GPIO  15
#define ECHO4_CONT  GPIO1
#define ECHO4_GPIO  14

// Initialize hardware
START:
    // Allow the PRU to access memories outside its own map
    // C4 is the addr of PRU_ICSS_CFG registers [see RG:10.1]
    LBCO r0, C4, 4, 4  // load 4 bytes from C4+4 (SYSCFG reg)  [RG:10.1.2]
    CLR r0, r0, 4      // clear bit 4 (enable OCP master ports?)
    SBCO r0, C4, 4, 4

    // Make constant 24 (c24) point to the beginning of PRU0 data ram
    // PRU_CTRL_REG base is 0x22000 (+20 is CTBIR0)
    MOV       r0, 0x00000000
    MOV       r1, 0x22020     // CTBIR0, constant block table index [RG:5.4.6]
    SBBO      r0, r1, 0, 4    // sets *both* C24 and C25 to 0?

    // Enable trigger as output and echo as input
    // NOTE! OE must be *cleared* for an output, set for input
    MOV r3, GPIO1 | GPIO_OE
    LBBO r2, r3, 0, 4
    CLR r2, 13          // trigger pin (GPIO1_13), set as output
    SET r2, 15          // echo pin (GPIO1_15), set as input
    SBBO r2, r3, 0, 4

    // clear data transfer space
    SBCO r0, c24, 0, 4   // pulse time
    SBCO r0, c24, 4, 4   // pre-pulse time
    SBCO r0, c24, 8, 4   // flag

    // Fire the sonar
TRIGGER:
    // Set trigger pin to high
    MOV r2, 1<<13
    MOV r3, GPIO1 | GPIO_SETDATAOUT
    SBBO r2, r3, 0, 4

    // Delay 10 microseconds (200 MHz / 2 instructions = 10 ns per loop, 10 us = 1000 loops)
    MOV r0, 1000

TRIGGER_DELAY_10US:
    SUB r0, r0, 1
    QBNE TRIGGER_DELAY_10US, r0, 0

    // Set trigger pin to low
    MOV r2, 1<<13
    MOV r3, GPIO1 | GPIO_CLEARDATAOUT
    SBBO r2, r3, 0, 4

    MOV r4, 0  // clear our main counter

    // Wait for the echo to go low, i.e. wait for the echo cycle to start
    MOV r3, GPIO1 | GPIO_DATAIN
WAIT_ECHO:
    // Read the GPIO in register
    LBBO r2, r3, 0, 4    // copy 4 bytes of GPIO1:DATAIN into r2

    ADD r4, r4, 1  // keep track of how long it takes to first see the pulse
    QBBC WAIT_ECHO, r2, 15  // loop while bit 15 is low

    SBCO r4, c24, 4, 4  // save pre-pulse count
    MOV r4, 0

    // Set r4 to zero, will be used to count the microseconds of the cho
SAMPLE_ECHO:
    // Read the GPIO in register
    LBBO r2, r3, 0, 4  // load GPIO1:DATAIN into r2

    //MOV r0, 79
    //QBGE SAMPLE_ECHO_DELAY_1US, r4, 5 // sample at least 5 times

    QBBC ECHO_COMPLETE, r2, 15  // break when bit 15 goes low

    // Bail if we've waited too long (15us, ~8ft)
    MOV r0, 15000
    QBLE ECHO_COMPLETE, r4, r0  // branch when 15000 < r4

    // Delay 1 microsecond between queries
    // Loop time is less than a 1us sicne it takes time to query the GPIO
    // register due to it not being within the local address space of the PRU
    MOV r0, 79   // loop 79 times (79 * 10ns = 0.79us)
SAMPLE_ECHO_DELAY_1US:
    SUB r0, r0, 1
    QBNE SAMPLE_ECHO_DELAY_1US, r0, 0

    // Add one to the microsecond counter
    ADD r4, r4, 1

    // Jump back to sampling the echo pin
    JMP SAMPLE_ECHO

    // When the echo is complete, do this
ECHO_COMPLETE:
    // Store the microsecond count in the PRU data ram
    SBCO r4, c24, 0, 4

    SBCO r2, c24, 8, 4  // save pins

    // Trigger the PRU0 interrupt (C program recognized the event)
    //   bit [0:3] are interrupt# - 16 (so PRU0_ARM_INT=19 => 3)
    //   bit 5 marks as valid
    MOV r31.b0, PRU0_ARM_INTERRUPT+16

    // Delay 33 milliseconds to allow sonar to stop resonating and for sound
    // burst to decay in environment
    MOV r0, 3300000
RESET_DELAY_33MS:
    SUB r0, r0, 1
    QBNE RESET_DELAY_33MS, r0, 0

    // Jump back to triggering the sonar
    JMP TRIGGER

