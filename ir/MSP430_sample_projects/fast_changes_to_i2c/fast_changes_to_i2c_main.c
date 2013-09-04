//NGOHARA
// 8/19/13

//******************************************************************************
//   MSP430 USCI I2C Transmitter and Receiver (Slave Mode)
//
//  Description: This code configures the MSP430's USCI module as
//  I2C slave capable of transmitting and receiving bytes.
//
//  ***THIS IS THE SLAVE CODE***
//
//                    Slave
//                 MSP430F2619
//             -----------------
//         /|\|              XIN|-
//          | |                 |
//          --|RST          XOUT|-
//            |                 |
//            |                 |
//            |                 |
//            |         SDA/P1.6|------->
//            |         SCL/P1.7|------->
//
// Note: External pull-ups are needed for SDA & SCL
//
// Uli Kretzschmar
// Texas Instruments Deutschland GmbH
// November 2007
// Built with IAR Embedded Workbench Version: 3.42A
//
//******************************************************************************
// Modified by S. Wendler, Mai 2013 to work with MSP430G2553 and msp-gcc
//******************************************************************************

#include "TI_USCI_I2C_slave.h"

#include <msp430.h>
#include "legacymsp430.h"
#include <msp430g2332.h>

void (*TI_receive_callback)(unsigned char receive);
void (*TI_transmit_callback)(unsigned char volatile *send_next);
void (*TI_start_callback)(void);

//------------------------------------------------------------------------------
// void TI_USCI_I2C_slaveinit(void (*SCallback)(),
//                            void (*TCallback)(unsigned char volatile *value),
//                            void (*RCallback)(unsigned char value),
//                            unsigned char slave_address)
//
// This function initializes the USCI module for I2C Slave operation.
//
// IN:   void (*SCallback)() => function is called when a START condition was detected
//       void (*TCallback)(unsigned char volatile *value) => function is called for every byte requested by master
//       void (*RCallback)(unsigned char value) => function is called for every byte that is received
//       unsigned char slave_address  =>  Slave Address
//------------------------------------------------------------------------------
void TI_USCI_I2C_slaveinit(void (*SCallback)(),
                           void (*TCallback)(unsigned char volatile *value),
                           void (*RCallback)(unsigned char value),
                           unsigned char slave_address)
{
    P1SEL |= SDA_PIN + SCL_PIN;               // Assign I2C pins to USCI_B0
    P1SEL2 |= SDA_PIN + SCL_PIN;              // Assign I2C pins to USCI_B0
    UCB0CTL1 |= UCSWRST;                      // Enable SW reset
    UCB0CTL0 = UCMODE_3 + UCSYNC;             // I2C Slave, synchronous mode
    UCB0I2COA = slave_address;                // set own (slave) address
    UCB0CTL1 &= ~UCSWRST;                     // Clear SW reset, resume operation
    IE2 |= UCB0TXIE + UCB0RXIE;               // Enable TX interrupt
    UCB0I2CIE |= UCSTTIE;                     // Enable STT interrupt
    TI_start_callback = SCallback;
    TI_receive_callback = RCallback;
    TI_transmit_callback = TCallback;
}

// USCI_B0 Data ISR
interrupt(USCIAB0TX_VECTOR) usci_i2c_data_isr(void)
{
    if (IFG2 & UCB0TXIFG)
        TI_transmit_callback(&UCB0TXBUF);
    else
        TI_receive_callback(UCB0RXBUF);
}

// USCI_B0 State ISR
interrupt(USCIAB0RX_VECTOR) usci_i2c_state_isr(void)
{
    UCB0STAT &= ~UCSTTIFG;                    // Clear start condition int flag
    TI_start_callback();
}
