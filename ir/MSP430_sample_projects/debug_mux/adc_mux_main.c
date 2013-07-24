//Current code demo
//NGOHARA 7/12/23

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

//Changed pin outs to work with pins needed for I2C
// P1.0	\\							XIN  \\
// P1.1 \\							XOUT \\
// P1.2 <-- ADC						Test \\
// P1.3 --> Debug Toggle			RDT  <--  Reset_Push
// P1.4 --> Sel_A					P1.7 -->  SDA
// P1.5 --> Sel_B					P1.6 <--  SCL
// P2.0	--> Sel_C					P2.5 --> LEDON_2 (IR array 2 on)
// P2.1 --> Sel_D					P2.4 --> LEDON_1 (IR array 1 on)
// P2.2 \\							P2.3 --> Inhibit (Mux_off)

//Next, removed all PWN and watchdog code, and put in following timer code

//******************************************************************************
//  MSP430G2xx2 Demo - Timer_A, Toggle P1.0, CCR0 Up Mode ISR, DCO SMCLK
//
//  Description: Toggle P1.0 using software and TA_0 ISR. Timer_A is
//  configured for up mode, thus the timer overflows when TAR counts to CCR0.
//  In this example CCR0 is loaded with 50000.
//  ACLK = n/a, MCLK = SMCLK = TACLK = default DCO
//
//
//           MSP430G2xx2
//         ---------------
//     /|\|            XIN|-
//      | |               |
//      --|RST        XOUT|-
//        |               |
//        |           P1.0|-->LED
//
//  D. Dang
//  Texas Instruments Inc.
//  December 2010
//  Built with CCS Version 4.2.0 and IAR Embedded Workbench Version: 5.10
//******************************************************************************



#include <msp430.h>

unsigned int adcvalue[32];	 //variable for storing current digital value of ADC input
int mem_num = 0;	//adcvalue array place

unsigned int ir_select = 0;	//variable for controlling 16b mux select

#define DIV_SIX		0x00AA		// 1/6 of 0x03FF for seven regions
#define TIMER		1000


// Store the adc value to memory, and
// handles the 16 bit analog mux with pins P1.4-7, inclusive.
void toggle_16b_mux(void){

	adcvalue[mem_num] = ADC10MEM;		//Question, am I reading before it's sampled?
	mem_num ++;
	if(mem_num >31){
		mem_num = 0;
		//P1OUT ^= BIT3; 		//Toggle P1.3 for frequency output
	}

	ir_select = ir_select+1;
	if(ir_select > 15) ir_select = 0;

	//  & Mask to clear select,  Mask and Shift Sel bits
	P1OUT = (P1OUT &  0x0F) + ((0x03 & ir_select) << 4);		//clears select bits, and or in new select
	P2OUT = (P2OUT &  0x3C) + ((0x0C & ir_select) >> 2);
}


//new main for timer
int main(void)
{
  WDTCTL = WDTPW + WDTHOLD;                 // Stop WDT

  //from I2C
  DCOCTL = 0;                               // Select lowest DCOx and MODx settings
  BCSCTL1 = CALBC1_16MHZ;               // Set DCO
  DCOCTL = CALDCO_16MHZ;

  BCSCTL2 |= ~SELS + +DIVS_0; 				//Set SMCLK to use DCOCLK

  //configure Port 1
  P1DIR |= BIT3 + BIT4 + BIT5;	// P1.3 for debug, 		P1.4,5 used for 16b mux select
  P1OUT = 0x00;									//initialize off
  P1OUT = 0xC0;                        // P1.6 & P1.7 Pullups
  P1REN |= 0xC0;                       // P1.6 & P1.7 Pullups

  //Configure Port 2 pins
    P2DIR = 0x3F;								// All six pins (P2.0-P2.5) output (though P2.2 unused)
    P2OUT = 0x00;								//Initialize all off
    P2REN = 0x00;								//No pullup resistors


  CCTL0 = CCIE;                             // CCR0 interrupt enabled
  CCR0 = TIMER;
  TACTL = TASSEL_2 + MC_1;                  // SMCLK, upmode

	//adc setup
	ADC10CTL0 = ADC10ON + ADC10SHT_0 + SREF_0 + ADC10IE;	//ADC on, 4*ADC10CLK, VCC&GND, Interrupt Enable
	ADC10AE0 |= BIT2;							//ADC enable for A2 (P1.2)
	ADC10CTL1 = INCH_2 + CONSEQ_0 ;          // Source P1.2, Use SMCLK,  1 source 1 conversion


	//Setup Enable Bits
	P2OUT |= BIT4 + BIT5;	//Inhibit (P2.3) =0, LEDON_1 and LEDON_2 (P2.4 and P2.5) = 1


  _BIS_SR(LPM0_bits + GIE);                 // Enter LPM0 w/ interrupt
}

// Timer A0 interrupt service routine
#pragma vector=TIMER0_A0_VECTOR
__interrupt void Timer_A (void)
{

	//For debug purposes, comment out when not in use.
	P1OUT ^= BIT3;					//Toggle P1.3 for frequency output

	ADC10CTL0 |= ENC + ADC10SC;             // Start sampling

	//Old visual with LEDs, removed for needed pins - NGOHARA 7/17/13
    //run_LEDS();		//performs adc save and changes LEDS



  	//For debug purposes, comment out when not in use.
  	//P1OUT ^= BIT3;					//Toggle P1.3 for frequency output
}


// ADC10 Interrupt service routine - NGOHARA 7/23/13
#pragma vector=ADC10_VECTOR
__interrupt void ADC10 (void)
{

	 toggle_16b_mux(); // handles mux select

	//For debug purposes, comment out when not in use.
	  	P1OUT ^= BIT3;					//Toggle P1.3 for frequency output

}








/*
 * old code
 *
void run_LEDS(void){

	adcvalue[mem_num] = ADC10MEM;
	mem_num ++;
	if(mem_num >31){
		mem_num = 0;
		//P1OUT ^= BIT3; 		//Toggle P1.3 for frequency output
	}


     //Six LEDS, scroll from OFF to all on on Port 2
     // will implement an input check, to turn off this function if not enabled
     switch(adcvalue[31]/DIV_SIX){
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
*/



//old main
/*
int main(void)
{
  WDTCTL = WDT_MDLY_0_064;                     // WDT interval timer, supposedly 0.064ms, or 15.625kHz
  	  	  	  	  	  	  	  	  	  	  	  //		(though scope seems to show between 2.76k and 3.33k)
  IE1 |= WDTIE;                             // Enable WDT interrupt

	//adc setup
  ADC10CTL0 = ADC10ON + ADC10SHT_2 + SREF_0;
  ADC10AE0 |= 0x01;                         // P1.0 ADC option select
  ADC10DTC1 = ADC10SSEL_0 + 0x001;          // 1 conversion

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
*/
