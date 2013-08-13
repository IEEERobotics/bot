//Uses demo seen below for basic code, more added later
//NGOHARA 7/2/13

//******************************************************************************
//  MSP430G2x32/G2x52 Demo - ADC10, DTC Sample A0 -> TA1, AVcc, DCO
//
//  Description: Use DTC to sample A0 with reference to AVcc and directly
//  transfer code to TACCR1. Timer_A has been configured for 10-bit PWM mode.
//  TACCR1 duty cycle is automatically proportional to ADC10 A0. WDT_ISR used
//  as a period wakeup timer approximately 45ms based on default ~1.2MHz
//  DCO/SMCLK clock source used in this example for the WDT clock source.
//  Timer_A also uses default DCO.
//
//                MSP430G2x32/G2x52
//             -----------------
//         /|\|              XIN|-
//          | |                 |
//          --|RST          XOUT|-
//            |                 |
//        >---|P1.0/A0      P1.2|--> TACCR1 - 0-1024 PWM
//
//  D. Dang
//  Texas Instruments Inc.
//  December 2010
//  Built with CCS Version 4.2.0 and IAR Embedded Workbench Version: 5.10
//******************************************************************************


// Added six "voltage bar LEDs" on Port 2
// Toggle on P1.3 outputs frequency of watchdog_timer and adc reads
// NGOHARA - 7/2/13


#include <msp430.h>

unsigned int adcvalue = 0; //variable for storing current digital value of ADC input
unsigned int adcvalue1 = 0;
unsigned int adcvalue2 = 0;
unsigned int adcvalue3 = 0;
unsigned int adcvalue4 = 0;

unsigned int ir_select = 0;	//variable for controlling 16b mux select

#define DIV_SIX		0x00AA		// 1/6 of 0x03FF for seven regions


void run_LEDS(void){

	//adcvalue(s) used for debugging, comment out when not in use;
    adcvalue4 = adcvalue3;
     adcvalue3 = adcvalue2;
     adcvalue2 = adcvalue1;
     adcvalue1 = adcvalue;
     adcvalue = ADC10MEM;

     //Six LEDS, scroll from OFF to all on on Port 2
     // will implement an input check, to turn off this function if not enabled
     switch(adcvalue/DIV_SIX){
     	 case 6: P2OUT = 0x3F;		// all ON
     	  	 break;
     	 case 5: P2OUT = 0x1F;		// 5 down ON
     	 	 break;
     	 case 4: P2OUT = 0x0F;		// 4 down ON
   	  	 	 break;
     	 case 3: P2OUT = 0x07;		// 3 down ON
   	  	 	 break;
     	 case 2: P2OUT = 0x03;		// 2 down ON
   	  	 	 break;
     	 case 1: P2OUT = 0x01;		// 1 down ON
   	  	 	 break;
     	 default: P2OUT = 0x00;	// all off
     }

}


// handles the 16 bit analog mux with pins P1.4-7, inclusive.
void toggle_16b_mux(void){

	ir_select = ir_select+1;
	if(ir_select > 15) ir_select = 0;

	P1OUT = (P1OUT &  0x0F) + (ir_select << 4);		//clears select bits, and or in new select
}



int main(void)
{
  WDTCTL = WDT_MDLY_0_064;                     // WDT interval timer, supposedly 0.064ms, or 15.625kHz
  	  	  	  	  	  	  	  	  	  	  	  //		(though scope seems to show between 2.76k and 3.33k)
  IE1 |= WDTIE;                             // Enable WDT interrupt

  ADC10CTL0 = ADC10SHT_2 + ADC10ON;
  ADC10AE0 |= 0x01;                         // P1.0 ADC option select
  ADC10DTC1 = 0x001;                        // 1 conversion

  P1DIR |= BIT2 + BIT4 + BIT5 + BIT6 + BIT7;	// P1.2 = output, 		P1.4-7 used for 16b mux select
  P1SEL |= 0x04;                            // P1.2 = TA1 output

  P1DIR |= BIT3;			//For debug purposes, comment out when not in use.

  //Configure Port 2 pins
   P2DIR = 0x3F;								// All six pins (P2.0-P2.5) output
   P2OUT = 0x00;								//Initialize all off (and mux in select 0)
   P2REN = 0x00;								//No pullup resistors

   //Configure PWM signal
  TACCR0 = 1024 - 1;                        // PWM Period
  TACCTL1 = OUTMOD_7;                       // TACCR1 reset/set
  TACCR1 = 512;                             // TACCR1 PWM Duty Cycle
  TACTL = TASSEL_2 + MC_1;                  // SMCLK, upmode

  while(1)
  {
    __bis_SR_register(LPM0_bits + GIE);     // LPM0, WDT_ISR will force exit
    //For debug purposes, comment out when not in use.
    P1OUT ^= BIT3;					//Toggle P1.3 for frequency output

    ADC10SA = (unsigned int)&TACCR1;        // Data transfer location
    ADC10CTL0 |= ENC + ADC10SC;             // Start sampling

    while (1) {				//Wait until adc interrupt flag is thrown, then disable flag and adc conversion
   		if (((ADC10CTL0 & ADC10IFG)==ADC10IFG)) {
   			ADC10CTL0 &= ~(ADC10IFG +ENC);
   			break;
   		}
    }



    run_LEDS();		//performs adc save and changes LEDS

    toggle_16b_mux(); // handles mux select

    //For debug purposes, comment out when not in use.
    P1OUT ^= BIT3;					//Toggle P1.3 for frequency output

      }
}

#pragma vector = WDT_VECTOR
__interrupt void WDT_ISR(void)
{
  __bic_SR_register_on_exit(LPM0_bits);     // Exit LPM0

}