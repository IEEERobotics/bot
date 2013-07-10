//***************************************************************************************
//  MSP430 Blink the LED Demo - Software Toggle P1.0
//
//  Description; Toggle P1.0 by xor'ing P1.0 inside of a software loop.
//  ACLK = n/a, MCLK = SMCLK = default DCO
//
//                MSP430x5xx
//             -----------------
//         /|\|              XIN|-
//          | |                 |
//          --|RST          XOUT|-
//            |                 |
//            |             P1.0|-->LED
//
//  J. Stevenson
//  Texas Instruments, Inc
//  July 2011
//  Built with Code Composer Studio v5
//***************************************************************************************

#include <msp430.h>				

void configureClocks();

int main(void) {
	WDTCTL = WDTPW | WDTHOLD;		// Stop watchdog timer

	configureClocks();				// Setup clocks at described freq

	P1DIR |= 0x01;					// Set P1.0 to output direction
	P1REN |= 0x00;					// Set P1.0 to pullup resistor 0ff (LEDs use external  390 ohm resistor)

	for(;;) {
		volatile unsigned int i;	// volatile to prevent optimization
		volatile unsigned int j;

		P1OUT ^= 0x01;				// Toggle P1.0 using exclusive-OR

		j = 10;
		i = 10000;					// SW Delay

		do{
			j--;

			do {
				i--;
			} while(i != 0);

		}while(j!=0);

	}

	return 0;
}

void configureClocks()
{
 // Set system DCO to 8MHz
 BCSCTL1 = CALBC1_8MHZ;
 DCOCTL = CALDCO_8MHZ;

 // Set LFXT1 to the VLO @ 12kHz
 BCSCTL3 |= LFXT1S_2;
 }


