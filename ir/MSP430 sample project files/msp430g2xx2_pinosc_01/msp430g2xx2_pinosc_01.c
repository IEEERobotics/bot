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
//  MSP430G2xx2 Demo - Capacitive Touch, Pin Oscillator Method, 1 button
//
//  Description: Basic 1-button input using the built-in pin oscillation feature
//  on GPIO input structure. PinOsc signal feed into TA0CLK. WDT interval is used
//  to gate the measurements. Difference in measurements indicate button touch.
//  LEDs flash if input is touched.
//  
//  ACLK = VLO = 12kHz, MCLK = SMCLK = 1MHz DCO
//
//               MSP430G2xx2
//             -----------------
//         /|\|              XIN|-
//          | |                 | 
//          --|RST          XOUT|-
//            |                 |
//            |             P1.1|<--Capacitive Touch Input 1
//            |                 |
//  LED 2  <--|P1.6             |
//            |                 |
//  LED 1  <--|P1.0             |
//            |                 |
//            |                 |
//
//  Brandon Elliott/D. Dang
//  Texas Instruments Inc.
//  November 2010
//  Built with IAR Embedded Workbench Version: 5.10
//******************************************************************************


#include <msp430.h>

/* Define User Configuration values */
/*----------------------------------*/
/* Defines WDT SMCLK interval for sensor measurements*/
#define WDT_meas_setting (DIV_SMCLK_512)
/* Defines WDT ACLK interval for delay between measurement cycles*/
#define WDT_delay_setting (DIV_ACLK_512)

/* Sensor settings*/
#define KEY_LVL     220                     // Defines threshold for a key press
/*Set to ~ half the max delta expected*/

/* Definitions for use with the WDT settings*/
#define DIV_ACLK_32768  (WDT_ADLY_1000)     // ACLK/32768
#define DIV_ACLK_8192   (WDT_ADLY_250)      // ACLK/8192 
#define DIV_ACLK_512    (WDT_ADLY_16)       // ACLK/512 
#define DIV_ACLK_64     (WDT_ADLY_1_9)      // ACLK/64 
#define DIV_SMCLK_32768 (WDT_MDLY_32)       // SMCLK/32768
#define DIV_SMCLK_8192  (WDT_MDLY_8)        // SMCLK/8192 
#define DIV_SMCLK_512   (WDT_MDLY_0_5)      // SMCLK/512 
#define DIV_SMCLK_64    (WDT_MDLY_0_064)    // SMCLK/64 

#define LED_1   (0x01)                      // P1.0 LED output
#define LED_2   (0x40)                      // P1.6 LED output

// Global variables for sensing
unsigned int base_cnt, meas_cnt;
int delta_cnt;
char key_pressed;
int cycles;
/* System Routines*/
void measure_count(void);                   // Measures each capacitive sensor
void pulse_LED(void);                       // LED gradient routine

/* Main Function*/
int main(void)
{ 
  unsigned int i,j;
  WDTCTL = WDTPW + WDTHOLD;                 // Stop watchdog timer
  if (CALBC1_1MHZ==0xFF)					// If calibration constants erased
  {											
    while(1);                               // do not load, trap CPU!!	
  }
  DCOCTL = 0;                               // Select lowest DCOx and MODx settings
  BCSCTL1 = CALBC1_1MHZ;                    // Set DCO to 1MHz
  DCOCTL =  CALDCO_1MHZ; 
  BCSCTL3 |= LFXT1S_2;                      // LFXT1 = VLO

  IE1 |= WDTIE;                             // enable WDT interrupt
  P2SEL = 0x00;                             // No XTAL 
  P1DIR = LED_1 + LED_2;                    // P1.0 & P1.6 = LEDs
  P1OUT = 0x00;                             

   __bis_SR_register(GIE);                  // Enable interrupts

  measure_count();                          // Establish baseline capacitance
    base_cnt = meas_cnt;

  for(i=15; i>0; i--)                       // Repeat and avg base measurement
  { 
    measure_count();
      base_cnt = (meas_cnt+base_cnt)/2;
  }
  

  /* Main loop starts here*/
  while (1)
  {
    j = KEY_LVL;
    key_pressed = 0;                        // Assume no keys are pressed

    measure_count();                        // Measure all sensors

 
      delta_cnt = base_cnt - meas_cnt;  // Calculate delta: c_change

      /* Handle baseline measurment for a base C decrease*/
      if (delta_cnt < 0)                    // If negative: result increased
      {                                     // beyond baseline, i.e. cap dec
          base_cnt = (base_cnt+meas_cnt) >> 1; // Re-average quickly
          delta_cnt = 0;                    // Zero out for pos determination
      }
      if (delta_cnt > j)                    // Determine if each key is pressed 
      {                                     // per a preset threshold
        j = delta_cnt;
        key_pressed = 1;                    // key pressed
      }
      else
        key_pressed = 1;

    /* Delay to next sample, sample more slowly if no keys are pressed*/
    if (key_pressed)
    {
      BCSCTL1 = (BCSCTL1 & 0x0CF) + DIVA_0; // ACLK/(0:1,1:2,2:4,3:8)
      cycles = 20;
    }
    else
    {
      cycles--;
      if (cycles > 0)
        BCSCTL1 = (BCSCTL1 & 0x0CF) + DIVA_0; // ACLK/(0:1,1:2,2:4,3:8)
      else
      {
        BCSCTL1 = (BCSCTL1 & 0x0CF) + DIVA_3; // ACLK/(0:1,1:2,2:4,3:8)
        cycles = 0;
      }
    }
    WDTCTL = WDT_delay_setting;             // WDT, ACLK, interval timer

    /* Handle baseline measurment for a base C increase*/
    if (!key_pressed)                       // Only adjust baseline down 
    {                                       // if no keys are touched
        base_cnt = base_cnt - 1;            // Adjust baseline down, should be 
    }                                       // slow to accomodate for genuine 
     pulse_LED();                           // changes in sensor C
   
    __bis_SR_register(LPM3_bits);
  }
}                                           // End Main

/* Measure count result (capacitance) of each sensor*/
/* Routine setup for four sensors, not dependent on NUM_SEN value!*/

void measure_count(void)
{ 
               
  TA0CTL = TASSEL_3+MC_2;                   // TACLK, cont mode
  TA0CCTL1 = CM_3+CCIS_2+CAP;               // Pos&Neg,GND,Cap


    /*Configure Ports for relaxation oscillator*/
    /*The P2SEL2 register allows Timer_A to receive it's clock from a GPIO*/
    /*See the Application Information section of the device datasheet for info*/
    P1DIR &= ~ BIT1;                        // P1.1 is the input used here
    P1SEL &= ~ BIT1;
    P1SEL2 |= BIT1;
    
    /*Setup Gate Timer*/
    WDTCTL = WDT_meas_setting;              // WDT, ACLK, interval timer
    TA0CTL |= TACLR;                        // Clear Timer_A TAR
    __bis_SR_register(LPM0_bits+GIE);       // Wait for WDT interrupt
    TA0CCTL1 ^= CCIS0;                      // Create SW capture of CCR1
    meas_cnt = TACCR1;                      // Save result
    WDTCTL = WDTPW + WDTHOLD;               // Stop watchdog timer
    P1SEL2 &= ~BIT1;


}

void pulse_LED(void)
{ 
  if(key_pressed)
  {
    P1OUT ^= LED_1 + LED_2;
  }else{
  P1OUT = 0;
  }
}
/* Watchdog Timer interrupt service routine*/
#pragma vector=WDT_VECTOR
__interrupt void watchdog_timer(void)
{
  TA0CCTL1 ^= CCIS0;                        // Create SW capture of CCR1
  __bic_SR_register_on_exit(LPM3_bits);     // Exit LPM3 on reti
}
