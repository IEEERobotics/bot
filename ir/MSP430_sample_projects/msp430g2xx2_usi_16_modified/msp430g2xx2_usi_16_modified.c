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
//  MSP430G2xx2 Demo - I2C Master Transmitter / Reciever, Repeated Start
//
//  Description: I2C Master communicates with I2C Slave using
//  the USI. Master data should increment from 0x55 with each transmitted byte
//  and Master determines the number of bytes transmitted and recieved, set by 
//  the Number_of_TX_Bytes and Number_of_RX_bytes values. These values will 
//  determine how many bytes are Txed then RXed with repeated starts in-between.
//  LED off for address or data Ack; LED on for address or data NAck.
//  ACLK = n/a, MCLK = SMCLK = Calibrated 1MHz
//
//
//  ***THIS IS THE MASTER CODE***
//
//                  Slave                      Master
//     (MSP430G2xx2_usi_15.c)
//             MSP430G2xx2         MSP430G2xx2
//             -----------------          -----------------
//         /|\|              XIN|-    /|\|              XIN|-
//          | |                 |      | |                 |
//          --|RST          XOUT|-     --|RST          XOUT|-
//            |                 |        |                 |
//      LED <-|P1.0             |        |                 |
//            |                 |        |             P1.0|-> LED
//            |         SDA/P1.7|------->|P1.6/SDA         |
//            |         SCL/P1.6|<-------|P1.7/SCL         |
//
//  Note: internal pull-ups are used in this example for SDA & SCL
//
//  D. Dang
//  Texas Instruments Inc.
//  December 2010
//  Built with CCS Version 4.2.0 and IAR Embedded Workbench Version: 5.10
//******************************************************************************

#include <msp430.h>


#define number_of_TX_bytes 2                // How many bytes do you want to TX?   
#define number_of_RX_bytes 3                // How many bytes do you want to RX?

void Master_RPT(void);

void Master_Transmit(void);
void Master_Recieve(void);

void Setup_USI_Master_TX(void);
void Setup_USI_Master_RX(void);

char MST_Data = 0x55;                       // Variable for transmitted data
char SLV_Addr = 0x90;                       
int I2C_State, Bytecount, Transmit, number_of_bytes, repeated_start = 0;     

void Data_TX (void);
void Data_RX (void);

int main(void)
{
  volatile unsigned int i;                  // Use volatile to prevent removal

  WDTCTL = WDTPW + WDTHOLD;                 // Stop watchdog
  if (CALBC1_1MHZ==0xFF)					// If calibration constant erased
  {											
    while(1);                               // do not load, trap CPU!!	
  }
  DCOCTL = 0;                               // Select lowest DCOx and MODx settings
  BCSCTL1 = CALBC1_1MHZ;                    // Set DCO
  DCOCTL = CALDCO_1MHZ;

  //BCSCTL2 = SELS; 				//Set SMCLK to use DCOCLK

  P1OUT = 0xC0;                             // P1.6 & P1.7 Pullups, others to 0
  P1REN |= 0xC0;                            // P1.6 & P1.7 Pullups
  P1DIR = 0xFF;                             // Unused pins as outputs
  P2OUT = 0;
  P2DIR = 0xFF;



  while(1)
  {

   Bytecount = 0;
   Master_RPT();

 }
}

/******************************************************
// USI interrupt service routine
// Data Transmit : state 0 -> 2 -> 4 -> 10 -> 12 -> 14
// Data Recieve  : state 0 -> 2 -> 4 -> 6 -> 8 -> 14
******************************************************/
#pragma vector = USI_VECTOR
__interrupt void USI_TXRX (void)
{
  switch(__even_in_range(I2C_State,14))
    {
      case 0: // Generate Start Condition & send address to slave
              P1OUT |= 0x01;                // LED on: sequence start
              Bytecount = 0;
              USISRL = 0x00;                // Generate Start Condition...
              USICTL0 |= USIGE+USIOE;
              USICTL0 &= ~USIGE;
              if (Transmit == 1){
                USISRL = 0x90;              // Address is 0x48 << 1 bit + 0 (rw)
              }
               if (Transmit == 0){
               USISRL = 0x91;               // 0x91 Address is 0x48 << 1 bit 
                                            // + 1 for Read
               }
              USICNT = (USICNT & 0xE0) + 0x08; // Bit counter = 8, TX Address
              I2C_State = 2;                // next state: rcv address (N)Ack
              break;

      case 2: // Receive Address Ack/Nack bit
              USICTL0 &= ~USIOE;            // SDA = input
              USICNT |= 0x01;               // Bit counter=1, receive (N)Ack bit
              I2C_State = 4;                // Go to next state: check (N)Ack
              break;

      case 4: // Process Address Ack/Nack & handle data TX
             
    	  	  if(Transmit == 1){
				  USICTL0 |= USIOE;             // SDA = output
				  if (USISRL & 0x01)            // If Nack received...
					  { // Send stop...
						USISRL = 0x00;
						USICNT |=  0x01;            // Bit counter=1, SCL high, SDA low
						I2C_State = 14;             // Go to next state: generate Stop
						P1OUT |= 0x01;              // Turn on LED: error
					  }

				  else
					  { // Ack received, TX data to slave...
					  USISRL = MST_Data++;            // Load data byte
					  USICNT |=  0x08;              // Bit counter = 8, start TX
					  I2C_State = 10;               // next state: receive data (N)Ack
					  Bytecount++;
					  P1OUT &= ~0x01;               // Turn off LED
					  break;
				  }
    	  	  }

    	  	  if(Transmit == 0){

				   if (USISRL & 0x01)            // If Nack received
				  { // Prep Stop Condition
					USICTL0 |= USIOE;
					USISRL = 0x00;
					USICNT |=  0x01;            // Bit counter= 1, SCL high, SDA low
					I2C_State = 8;              // Go to next state: generate Stop
					P1OUT |= 0x01;              // Turn on LED: error
				  }
				  else{ Data_RX();}             // Ack received


    	  	  }
              break;

case 6: // Send Data Ack/Nack bit      
              USICTL0 |= USIOE;             // SDA = output
              if (Bytecount <= number_of_bytes-2)
              {                             // If this is not the last byte
                USISRL = 0x00;              // Send Ack
                P1OUT &= ~0x01;             // LED off
                I2C_State = 4;              // Go to next state: data/rcv again
                Bytecount++;
                }
                
              else //last byte: send NACK
              {
                USISRL = 0xFF;              // Send NAck
                P1OUT |= 0x01;              // LED on: end of comm
                I2C_State = 8;              // stop condition
              }
              USICNT |= 0x01;               // Bit counter = 1, send (N)Ack bit
              break;

      case 8: // Prep Stop Condition
              USICTL0 |= USIOE;             // SDA = output
              USISRL = 0x00;
              USICNT |=  0x01;              // Bit counter= 1, SCL high, SDA low
              I2C_State = 14;               // Go to next state: generate Stop
              break;

      case 10: // Receive Data Ack/Nack bit
              USICTL0 &= ~USIOE;            // SDA = input
              USICNT |= 0x01;               // Bit counter = 1, receive (N)Ack bit
              I2C_State = 12;               // Go to next state: check (N)Ack
              break;

      case 12: // Process Data Ack/Nack & send Stop
                    
              USICTL0 |= USIOE;
              if (Bytecount == number_of_bytes){// If last byte
                
                if(repeated_start == 1){
                
                USISRL = 0xFF;                // this will prevent a stop cond
                USICTL0 |= USIOE;             // SDA = output
                I2C_State = 14;               // Go to next state: generate Stop
                USICNT |=  0x01;     }        // set count=1 to trigger next state
                
              else{
              USISRL = 0x00;
              
              I2C_State = 14;               // Go to next state: generate Stop
              P1OUT |= 0x01;
              USICNT |=  0x01;     }        // set count=1 to trigger next state
              }else{
                P1OUT &= ~0x01;             // Turn off LED
                Data_TX();                  // TX byte
              }
              break;

      case 14:// Generate Stop Condition
              USISRL = 0x0FF;               // USISRL = 1 to release SDA
              USICTL0 |= USIGE;             // Transparent latch enabled
              USICTL0 &= ~(USIGE+USIOE);    // Latch/SDA output disabled
              I2C_State = 0;                // Reset state machine for next xmt
              LPM0_EXIT;                    // Exit active for next transfer
              break;
    }

  USICTL1 &= ~USIIFG;                       // Clear pending flag
}
// END interrupt USI_TXRX -------------------------------------------------------------------------------------------------


void Data_TX (void){

              USISRL = MST_Data++;          // Load data byte
              USICNT |=  0x08;              // Bit counter = 8, start TX
              I2C_State = 10;               // next state: receive data (N)Ack
              Bytecount++;
}

void Data_RX (void){
	USICTL0 &= ~USIOE;                  // SDA = input --> redundant
        USICNT |=  0x08;                    // Bit counter = 8, RX data
        I2C_State = 6;                      // Next state: Test data and (N)Ack
        P1OUT &= ~0x01;                     // LED off
        }


void Setup_USI_Master_TX (void)
{ 
  _DINT();
  Transmit = 1;
  USICTL0 = USIPE6+USIPE7+USIMST+USISWRST;  // Port & USI mode setup
  USICTL1 = USII2C+USIIE;                   // Enable I2C mode & USI interrupt
  USICKCTL = USIDIV_7+USISSEL_2+USICKPL;    // USI clk: SCL = SMCLK/128
  USICNT |= USIIFGCC;                       // Disable automatic clear control
  USICTL0 &= ~USISWRST;                     // Enable USI
  USICTL1 &= ~USIIFG;                       // Clear pending flag
  _EINT();
}


void Setup_USI_Master_RX (void)
{ 
  _DINT();
  Transmit = 0;
  USICTL0 = USIPE6+USIPE7+USIMST+USISWRST;  // Port & USI mode setup
  USICTL1 = USII2C+USIIE;                   // Enable I2C mode & USI interrupt
  USICKCTL = USIDIV_7+USISSEL_2+USICKPL;    // USI clks: SCL = SMCLK/128
  USICNT |= USIIFGCC;                       // Disable automatic clear control
  USICTL0 &= ~USISWRST;                     // Enable USI
  USICTL1 &= ~USIIFG;                       // Clear pending flag
  _EINT();

}

void Master_Transmit(void){
  number_of_bytes = number_of_TX_bytes;
Setup_USI_Master_TX();
    USICTL1 |= USIIFG;                      // Set flag and start communication
    LPM0;                                   // CPU off, await USI interrupt
}
void Master_Recieve(void){
  number_of_bytes = number_of_RX_bytes;
  Setup_USI_Master_RX();
  USICTL1 |= USIIFG;                        // Set flag and start communication
  LPM0;                                     // CPU off, await USI interrupt
}

void Master_RPT(void){
    repeated_start =1;                    

    Master_Transmit();
    _NOP();                                 
  
    Master_Recieve();
    _NOP();

    repeated_start =0;

}
