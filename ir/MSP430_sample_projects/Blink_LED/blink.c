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

int main(void) {
	WDTCTL = WDTPW | WDTHOLD;		// Stop watchdog timer
	P1DIR |= 0x41;					// Set P1.0 and P1.6 to output direction


	P1OUT = 0x40;	//initialize P1.0 off, P1.6 on for alternate blink


	for(;;) {
		volatile unsigned int i;	// volatile to prevent optimization

		P1OUT ^= 0x41;				// Toggle P1.0 and P1.6 using exclusive-OR


		i = 100000;					// SW Delay
		do i--;
		while(i != 0);
	}
	
	return 0;
}
