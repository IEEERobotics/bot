// Define the entry point of the program
.origin 0
.entrypoint START

// Base addresses of the low-level GPIO controllers
//  GPIO0: 0-31
//  GPIO1: 32-63, etc
#define GPIO0  0x44e07000
#define GPIO1  0x4804c000
#define GPIO2  0x481ac000
#define GPIO3  0x481ae000

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

// Echo pins should be in pinmode 0x27 (mode 7 pulldown)

// Front Trig: P9_25
#define TRIG1_GPIO  GPIO3
#define TRIG1_PIN   21
// Front Echo: P9_23 (0x844)
#define ECHO1_GPIO  GPIO1
#define ECHO1_PIN   17

// Back Trig: P8_11
#define TRIG2_GPIO  GPIO1
#define TRIG2_PIN   13
// Back Echo: P8_15 (0x83c)
#define ECHO2_GPIO  GPIO1
#define ECHO2_PIN   15

// Left Trig: P9_30
#define TRIG3_GPIO  GPIO3
#define TRIG3_PIN   16
// Left Echo: P9_28 (0x99c)
#define ECHO3_GPIO  GPIO3
#define ECHO3_PIN   17

// Right Trig: P9_29
#define TRIG4_GPIO  GPIO3
#define TRIG4_PIN   15
// Right Echo: P9_31 (0x990)
#define ECHO4_GPIO  GPIO3
#define ECHO4_PIN   14

.macro gpio_output
.mparam gpio, pin
    // NOTE! OE must be *cleared* for an output
    MOV   r3, gpio | GPIO_OE
    LBBO  r2, r3, 0, 4
    CLR   r2, pin
    SBBO  r2, r3, 0, 4
.endm

.macro gpio_input
.mparam gpio, pin
    // NOTE! OE must be *set* for an input
    MOV   r3, gpio | GPIO_OE
    LBBO  r2, r3, 0, 4
    SET   r2, pin
    SBBO  r2, r3, 0, 4
.endm

.macro gpio_low
.mparam gpio, pin
    SET r2, pin
    MOV r0, GPIO_CLEARDATAOUT
    OR  r3, gpio, r0
    SBBO r2, r3, 0, 4
.endm

.macro gpio_high
.mparam gpio, pin
    SET r2, pin
    MOV r0, GPIO_SETDATAOUT
    OR  r3, gpio, r0
    SBBO r2, r3, 0, 4
.endm

// approx 25ns + LBBO(~165ns?) = 190ns
.macro gpio_read
.mparam gpio, pin
    MOV  r1, GPIO_DATAIN
    OR   r1, r1, gpio
    LBBO r2, r1, 0, 4  // copy 4 bytes from GPIO1:DATAIN into r2
    SET  r1, pin
    AND  r0, r2, r1    // select pin value
    LSR  r0, r0, pin
.endm


// Initialize hardware
START:
    // Allow the PRU to access memories outside its own map
    // C4 is the addr of PRU_ICSS_CFG registers [see RG:10.1]
    LBCO  r0, C4, 4, 4  // load 4 bytes from C4+4 (SYSCFG reg)  [RG:10.1.2]
    CLR   r0, r0, 4      // clear bit 4 (enable OCP master ports?)
    SBCO  r0, C4, 4, 4

    // Make constant 24 (c24) point to the beginning of PRU0 data ram (0x00)
    // PRU_CTRL_REG base is 0x22000 (+20 is CTBIR0)
    MOV   r0, 0x00000000
    MOV   r1, 0x22020     // CTBIR0, constant block table index [RG:5.4.6]
    SBBO  r0, r1, 0, 4    // sets *both* C24 and C25 to 0?

    gpio_output TRIG1_GPIO, TRIG1_PIN
    gpio_input  ECHO1_GPIO, ECHO1_PIN
    gpio_output TRIG2_GPIO, TRIG2_PIN
    gpio_input  ECHO2_GPIO, ECHO2_PIN
    gpio_output TRIG3_GPIO, TRIG3_PIN
    gpio_input  ECHO3_GPIO, ECHO3_PIN
    gpio_output TRIG4_GPIO, TRIG4_PIN
    gpio_input  ECHO4_GPIO, ECHO4_PIN

    // zero the data region we plan to use
    MOV   r0, 0   // 4 bytes of data to initialize with
    MOV   r1, 0   // addr counter
    LOOP END_INIT_MEM, 8  // clear 8 words
        SBCO  r0, c24, r1, 4   // pulse time
        ADD   r1, r1, 4
    END_INIT_MEM:

.struct sUltrasonic
    .u32  trigGPIO
    .u32  echoGPIO
    .u32  dataOffset
    .u8   trigPin
    .u8   echoPin
.ends

.assign sUltrasonic, r5, r8.w0, Ultrasonic


READ_ALL:
    MOV  Ultrasonic.trigGPIO, TRIG1_GPIO
    MOV  Ultrasonic.trigPin, TRIG1_PIN
    MOV  Ultrasonic.echoGPIO, ECHO1_GPIO
    MOV  Ultrasonic.echoPin, ECHO1_PIN
    MOV  Ultrasonic.dataOffset, 0
    CALL READ_SENSOR
    CALL RESET_DELAY

    MOV  Ultrasonic.trigGPIO, TRIG2_GPIO
    MOV  Ultrasonic.trigPin, TRIG2_PIN
    MOV  Ultrasonic.echoGPIO, ECHO2_GPIO
    MOV  Ultrasonic.echoPin, ECHO2_PIN
    MOV  Ultrasonic.dataOffset, 8
    CALL READ_SENSOR
    CALL RESET_DELAY

    MOV  Ultrasonic.trigGPIO, TRIG3_GPIO
    MOV  Ultrasonic.trigPin, TRIG3_PIN
    MOV  Ultrasonic.echoGPIO, ECHO3_GPIO
    MOV  Ultrasonic.echoPin, ECHO3_PIN
    MOV  Ultrasonic.dataOffset, 16
    CALL READ_SENSOR
    CALL RESET_DELAY

    MOV  Ultrasonic.trigGPIO, TRIG4_GPIO
    MOV  Ultrasonic.trigPin, TRIG4_PIN
    MOV  Ultrasonic.echoGPIO, ECHO4_GPIO
    MOV  Ultrasonic.echoPin, ECHO4_PIN
    MOV  Ultrasonic.dataOffset, 24
    CALL READ_SENSOR
    CALL RESET_DELAY

    // Trigger the PRU0 interrupt (C program recognized the event)
    //   bit [0:3] are interrupt# - 16 (so PRU0_ARM_INT=19 => 3)
    //   bit 5 marks as valid
    MOV r31.b0, PRU0_ARM_INTERRUPT+16

    JMP READ_ALL

    // Delay 33 milliseconds to allow sonar to stop resonating and for sound
    // burst to decay in environment
RESET_DELAY:
    MOV r0, 3300000
DELAY_LOOP:
    SUB r0, r0, 1
    QBNE DELAY_LOOP, r0, 0
    RET

    // Fire the sonar
READ_SENSOR:
    gpio_high Ultrasonic.trigGPIO, Ultrasonic.trigPin
    // Delay 10 microseconds (200 MHz / 2 instructions = 10 ns per loop, 10 us = 1000 loops)
    MOV r0, 1000

TRIGGER_DELAY_10US:
    SUB r0, r0, 1
    QBNE TRIGGER_DELAY_10US, r0, 0

    gpio_low Ultrasonic.trigGPIO, Ultrasonic.trigPin
    MOV r4, 0  // clear our main counter

    // Wait for the echo to go high, i.e. wait for the echo cycle to start
WAIT_ECHO:
    ADD r4, r4, 1  // keep track of how long it takes to first see the pulse

    MOV r0, 3000
    QBLE NO_ECHO, r4, r0  // fail when 3000 < r4

    gpio_read Ultrasonic.echoGPIO, Ultrasonic.echoPin // reads value of pin into r0
    QBEQ WAIT_ECHO, r0, 0  // loop while bit is low

    // save pre-pulse count
    ADD r0, Ultrasonic.dataOffset, 4
    SBCO r4, c24, r0, 4

    MOV r4, 0           // zero pulse time (us) counter
    // loop time gpio_read(~190ns) + 4 ops(20ns) + 780ns + (2ops) 10ns  = 1000ns
SAMPLE_ECHO:
    gpio_read Ultrasonic.echoGPIO, Ultrasonic.echoPin // reads value of pin into r0 (190ns)
    QBEQ ECHO_COMPLETE, r0, 0  // break when bit 15 goes low

    // Bail if we've waited too long (25us, ~14ft)
    MOV r0, 25000
    QBLE ECHO_COMPLETE, r4, r0  // branch when 25000 < r4

    // Delay 1 microsecond between queries
    // Loop time is less than a 1us sicne it takes time to query the GPIO
    // register due to it not being within the local address space of the PRU
    MOV r0, 78   // loop 79 times (79 * 10ns = 0.79us)
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

    SBCO r4, c24, Ultrasonic.dataOffset, 4
    RET

// We never saw an echo pulse  =(
NO_ECHO:
    MOV r4, 99999
    ADD r0, Ultrasonic.dataOffset, 4
    SBCO r4, c24, r0, 4
    RET

