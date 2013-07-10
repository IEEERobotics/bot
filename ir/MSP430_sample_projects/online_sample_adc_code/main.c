//http://intro2launchpad.wikispaces.com/ADC
//ngohara 6/20/2013
// attempting to learn adc code
//

#include "msp430g2332.h"
#define INPUT_1 INCH_4
#define INPUT_2 INCH_5

unsigned int adcvalue1 = 0; //variable for storing digital value of CH4 input
unsigned int adcvalue2 = 0; //variable for storing digital value of CH5 input

unsigned int analogRead(unsigned int pin) {
	ADC10CTL0 = ADC10ON + ADC10SHT_2 + SREF_0;
	ADC10CTL1 = ADC10SSEL_0 + pin;

		if (pin==INCH_4){
			ADC10AE0 = 0x10;
		}
		else if(pin==INCH_5){
			ADC10AE0 = 0x20;
		}
		ADC10CTL0 |= ENC + ADC10SC;

		while (1) {
			if (((ADC10CTL0 & ADC10IFG)==ADC10IFG)) {
				ADC10CTL0 &= ~(ADC10IFG +ENC);
			break;
		}
	}
	return ADC10MEM;
}


void main(void) {

	WDTCTL = WDTPW + WDTHOLD; 	//Stop Watchdog Timer
	P1DIR = 0x41; 				//P1.0=>LED1 and P1.1=>LED2

	while (1){
		adcvalue1 = analogRead( INPUT_1 ); 	//Read the analog input from channel 4
		adcvalue2 = analogRead( INPUT_2 ); 	//Read the analog input from channel 5

		if ((adcvalue1>=adcvalue2)){
		P1OUT = BIT6; 		//Glow LED2 if channel4 input > channel5 input
		}
		if ((adcvalue2>adcvalue1)) {
		P1OUT = BIT0; 		//Glow LED1 if channel4 input > channel5 input
	}
	}

}
