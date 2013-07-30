//  See Bottom of File for TI MSP430 Copyright and Disclaimer
//
//  MSP430G2xx2 Demo - P1 Interrupt from LPM4 with Internal Pull-up
//		modified to read ADC on A1 ie P1.1
//		then toggles LED(s) on value
//
//
//  Description: A hi/low transition on P1.4 will trigger P1_ISR which,
//  toggles P1.0. Normal mode is LPM4 ~ 0.1uA.
//  Internal pullup enabled on P1.4.
//  ACLK = n/a, MCLK = SMCLK = default DCO
//
//               MSP430G2xx2
//            -----------------
//        /|\|              XIN|-
//         | |                 |
//         --|RST          XOUT|-
//     /|\   |      R          |
//      --o--| P1.3-o      P1.0|-->LED1
//     \|/   |			   P1.1|<-- voltage
//			 |			   P1.6|--> LED2
//
//  D. Dang
//  Texas Instruments Inc.
//  December 2010
//  Built with CCS Version 4.2.0 and IAR Embedded Workbench Version: 5.10
//******************************************************************************

#include <msp430.h>
#define INPUT_0 INCH_1 		//Selects channel A1
#define INPUT_1 INCH_4		//Selects channel A4
#define INPUT_2 INCH_5		//Selects channel A5

#define VOLTAGE_HALF	0x01FF		//Half of 0x03FF
#define DIV_SIX		0x00AA		// 1/6 of 0x03FF for seven regions

unsigned int adcvalue = 0; //variable for storing current digital value of ADC input
unsigned int adcvalue1 = 0;
unsigned int adcvalue2 = 0;
unsigned int adcvalue3 = 0;
unsigned int adcvalue4 = 0;

unsigned int analogRead(unsigned int pin) {
	ADC10CTL0 = ADC10ON + ADC10SHT_2 + SREF_0;
	ADC10CTL1 = ADC10SSEL_0 + pin;


		if (pin==INCH_4){
			ADC10AE0 = 0x10;	//select A4 as input
		}
		else if(pin==INCH_5){
			ADC10AE0 = 0x20;	//select A5 as input
		}
		else if(pin == INCH_1){
			ADC10AE0 = 0x02;	//select A1 as input
		}

		ADC10CTL0 |= ENC + ADC10SC;

		while (1) {				//Wait until adc interrupt flag is thrown, then disable flag and adc conversion
			if (((ADC10CTL0 & ADC10IFG)==ADC10IFG)) {
				ADC10CTL0 &= ~(ADC10IFG +ENC);
			break;
		}
	}
	return ADC10MEM;
}

int main(void)
{
  WDTCTL = WDTPW + WDTHOLD;                 // Stop watchdog timer

  //setup ADC settings  //actually initialize in read function
  //ADC10CTL0 = ADC10SHT_2 + ADC10ON ;		 // ADC10ON
  //ADC10CTL1 = INCH_1;                       // input A1 (i.e. P1.1)
  //ADC10AE0 = 0x02;                         // PA.1 ADC option select

  //configure Port 1 pins
  P1DIR = BIT0 + BIT6;                       // P1.0 and P1.6 output, else input
  P1OUT =  0x08;                            // P1.3 set, else reset
  P1REN |= 0x08;                            // P1.3 pull-up
  //Configure Port 2 pins
  P2DIR = 0x3F;								// All six pins (P2.0-P2.5) output
  P2OUT = 0x00;								//Initialize all off
  P2REN = 0x00;								//No pullup resistors
  //Config switch interupt
  P1IE |= 0x08;                             // P1.3 interrupt enabled
  P1IES |= 0x08;                            // P1.3 Hi/lo edge
  P1IFG &= ~0x08;                           // P1.3 IFG cleared

  _BIS_SR(LPM4_bits + GIE);                 // Enter LPM4 w/interrupt
}





// Port 1 interrupt service routine
#pragma vector=PORT1_VECTOR
__interrupt void Port_1(void)
{
  P1OUT ^= 0x01;                            // P1.0 = toggle for switch press
  P1IFG &= ~0x08;                           // P1.3 IFG cleared

  adcvalue4 = adcvalue3;
  adcvalue3 = adcvalue2;
  adcvalue2 = adcvalue1;
  adcvalue1 = adcvalue;
  adcvalue = analogRead( INPUT_0 ); //only need input on P1.1

  /*//Break ADC into halves and display on LED on P1.6
  if(adcvalue > VOLTAGE_HALF){
	  P1OUT |= BIT6;                            // P1.6 on for high adc value
  }
  else {
	  P1OUT &= ~BIT6;                            // P1.6 on for high adc value
  }
	*/


  //Six LEDS, scroll from OFF to all on on Port 2
  // will implement an input check, to turn off this function if not enabled
  switch(adcvalue/DIV_SIX){
  	  case 6: P2OUT = 0x3F;		// all on
  	  	  break;
  	  case 5: P2OUT = 0x1F;		// 5 down on
	  	  break;
  	  case 4: P2OUT = 0x0F;		// 4 down on
	  	  break;
  	  case 3: P2OUT = 0x07;		// 3 down on
	  	  break;
  	  case 2: P2OUT = 0x03;		// 2 down on
	  	  break;
  	  case 1: P2OUT = 0x01;		// 1 down on
	  	  break;
  	  default: P2OUT = 0x00;	// all off
  }
}









/* --COPYRIGHT--,BSD_EX
 * Copyright (c) 2012, Texas Instruments Incorporated
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *******************************************************************************
 *
 *                       MSP430 CODE EXAMPLE DISCLAIMER
 *
 * MSP430 code examples are self-contained low-level programs that typically
 * demonstrate a single peripheral function or device feature in a highly
 * concise manner. For this the code may rely on the device's power-on default
 * register values and settings such as the clock configuration and care must
 * be taken when combining code from several examples to avoid potential side
 * effects. Also see www.ti.com/grace for a GUI- and www.ti.com/msp430ware
 * for an API functional library-approach to peripheral configuration.
 *
 * --/COPYRIGHT--*/
//******************************************************************************
