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
//  MSP430G2xx2 Demo - I2C Master Receiver, single byte
//
//  Description: I2C Master communicates with I2C Slave using
//  the USI. Slave data should increment from 0x00 with each transmitted byte
//  which is verified by the Master.
//  LED off for address or data Ack; LED on for address or data NAck.
//  ACLK = n/a, MCLK = SMCLK = Calibrated 1MHz
//
//  ***THIS IS THE MASTER CODE***
//
//                  Slave                      Master
//          (MSP430G2xx2_usi_09.c)
//            MSP430G2xx2           MSP430G2xx2
//             -----------------          -----------------
//         /|\|              XIN|-    /|\|              XIN|-
//          | |                 |      | |                 |
//          --|RST          XOUT|-     --|RST          XOUT|-
//            |                 |        |                 |
//      LED <-|P1.0             |        |                 |
//            |                 |        |             P1.0|-> LED
//            |         SDA/P1.7|------->|P1.7/SDA         |
//            |         SCL/P1.6|<-------|P1.6/SCL         |
//
//  Note: internal pull-ups are used in this example for SDA & SCL
//
//  D. Dang
//  Texas Instruments Inc.
//  December 2010
//  Built with CCS Version 4.2.0 and IAR Embedded Workbench Version: 5.10
//******************************************************************************

#include <msp430.h>


char SLV_data = 0x00;                  // Variable for received data
char SLV_Addr = 0x91;                  // Address is 0x48 << 1 bit + 1 for Read
int I2C_State = 0;                     // State variable

int main(void)
{
  volatile unsigned int i;             // Use volatile to prevent removal

  WDTCTL = WDTPW + WDTHOLD;            // Stop watchdog
  if (CALBC1_1MHZ==0xFF)			   // If calibration constants erased
  {											
    while(1);                          // do not load, trap CPU!!	
  }
  DCOCTL = 0;                               // Select lowest DCOx and MODx settings
  BCSCTL1 = CALBC1_1MHZ;               // Set DCO
  DCOCTL = CALDCO_1MHZ;

  P1OUT = 0xC0;                        // P1.6 & P1.7 Pullups
  P1REN |= 0xC0;                       // P1.6 & P1.7 Pullups
  P1DIR = 0xFF;                        // Unused pins as outputs
  P2OUT = 0;
  P2DIR = 0xFF;

  USICTL0 = USIPE6+USIPE7+USIMST+USISWRST;// Port & USI mode setup
  USICTL1 = USII2C+USIIE;              // Enable I2C mode & USI interrupt
  USICKCTL = USIDIV_3+USISSEL_2+USICKPL;// Setup USI clocks: SCL = SMCLK/8 (~120kHz)
  USICNT |= USIIFGCC;                  // Disable automatic clear control
  USICTL0 &= ~USISWRST;                // Enable USI
  USICTL1 &= ~USIIFG;                  // Clear pending flag
  _EINT();

  while(1)
  {
    USICTL1 |= USIIFG;                 // Set flag and start communication
    LPM0;                              // CPU off, await USI interrupt
    _NOP();                            // Used for IAR
    for (i = 0; i < 5000; i++);        // Dummy delay between communication cycles
  }
}



/******************************************************
// USI interrupt service routine
******************************************************/
#pragma vector = USI_VECTOR
__interrupt void USI_TXRX (void)
{
  switch(I2C_State)
    {
      case 0: // Generate Start Condition & send address to slave
              P1OUT |= 0x01;           // LED on: sequence start
              USISRL = 0x00;           // Generate Start Condition...
              USICTL0 |= USIGE+USIOE;
              USICTL0 &= ~USIGE;
              USISRL = SLV_Addr;       // ... and transmit address, R/W = 1
              USICNT = (USICNT & 0xE0) + 0x08; // Bit counter = 8, TX Address
              I2C_State = 2;           // Go to next state: receive address (N)Ack
              break;

      case 2: // Receive Address Ack/Nack bit
              USICTL0 &= ~USIOE;       // SDA = input
              USICNT |= 0x01;          // Bit counter = 1, receive (N)Ack bit
              I2C_State = 4;           // Go to next state: check (N)Ack
              break;

      case 4: // Process Address Ack/Nack & handle data RX
              if (USISRL & 0x01)       // If Nack received...
              { // Prep Stop Condition
                USICTL0 |= USIOE;
                USISRL = 0x00;
                USICNT |=  0x01;       // Bit counter = 1, SCL high, SDA low
                I2C_State = 10;        // Go to next state: generate Stop
                P1OUT |= 0x01;         // Turn on LED: error
              }
              else                     // Ack received
              { // Receive Data from slave
                USICNT |=  0x08;       // Bit counter = 8, RX data
                I2C_State = 6;         // Go to next state: Test data and (N)Ack
                P1OUT &= ~0x01;        // LED off
              }
              break;

      case 6: // Send Data Ack/Nack bit
              USICTL0 |= USIOE;        // SDA = output
              if (USISRL == SLV_data)  // If data valid...
              {
                USISRL = 0x00;         // Send Ack
                SLV_data++;            // Increment Slave data
                P1OUT &= ~0x01;        // LED off
              }
              else
              {
                USISRL = 0xFF;         // Send NAck
                P1OUT |= 0x01;         // LED on: error
              }
              USICNT |= 0x01;          // Bit counter = 1, send (N)Ack bit
              I2C_State = 8;           // Go to next state: prep stop
              break;

      case 8: // Prep Stop Condition
              USICTL0 |= USIOE;        // SDA = output
              USISRL = 0x00;
              USICNT |=  0x01;         // Bit counter = 1, SCL high, SDA low
              I2C_State = 10;          // Go to next state: generate Stop
              break;

      case 10: // Generate Stop Condition
              USISRL = 0x0FF;          // USISRL = 1 to release SDA
              USICTL0 |= USIGE;        // Transparent latch enabled
              USICTL0 &= ~(USIGE+USIOE);// Latch/SDA output disabled
              I2C_State = 0;           // Reset state machine for next transmission
              LPM0_EXIT;               // Exit active for next transfer
              break;
    }

  USICTL1 &= ~USIIFG;                  // Clear pending flag
}
