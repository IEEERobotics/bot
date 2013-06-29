/*
 *  Do not modify this file; it is automatically 
 *  generated and any modifications will be overwritten.
 *
 * @(#) xdc-z44
 */

#define __nested__
#define __config__

#include <xdc/std.h>

/*
 * ======== GENERATED SECTIONS ========
 *     
 *     MODULE INCLUDES
 *     
 *     <module-name> INTERNALS
 *     <module-name> INHERITS
 *     <module-name> VTABLE
 *     <module-name> PATCH TABLE
 *     <module-name> DECLARATIONS
 *     <module-name> OBJECT OFFSETS
 *     <module-name> TEMPLATES
 *     <module-name> INITIALIZERS
 *     <module-name> FUNCTION STUBS
 *     <module-name> PROXY BODY
 *     <module-name> OBJECT DESCRIPTOR
 *     <module-name> SYSTEM FUNCTIONS
 *     <module-name> PRAGMAS
 *     
 *     INITIALIZATION ENTRY POINT
 *     PROGRAM GLOBALS
 *     CLINK DIRECTIVES
 */


/*
 * ======== MODULE INCLUDES ========
 */



/*
 * ======== xdc.cfg.Program TEMPLATE ========
 */

/*
 *  ======== __ASM__ ========
 *  Define absolute path prefix for this executable's
 *  configuration generated files.
 */
xdc__META(__ASM__, "@(#)__ASM__ = C:/Users/Neal/Dropbox/IR_Array/MSP430 sample project files/g2332_grace_adc_push_demo/Debug/configPkg/package/cfg/main_pe430");

/*
 *  ======== __ISA__ ========
 *  Define the ISA of this executable.  This symbol is used by platform
 *  specific "exec" commands that support more than one ISA; e.g., gdb
 */
xdc__META(__ISA__, "@(#)__ISA__ = 430");

/*
 *  ======== __PLAT__ ========
 *  Define the name of the platform that can run this executable.  This
 *  symbol is used by platform independent "exec" commands
 */
xdc__META(__PLAT__, "@(#)__PLAT__ = ti.platforms.msp430");

/*
 *  ======== __TARG__ ========
 *  Define the name of the target used to build this executable.
 */
xdc__META(__TARG__, "@(#)__TARG__ = ti.targets.msp430.elf.MSP430");

/*
 *  ======== __TRDR__ ========
 *  Define the name of the class that can read/parse this executable.
 */
xdc__META(__TRDR__, "@(#)__TRDR__ = ti.targets.omf.elf.Elf32");


/*
 * ======== xdc.cfg.SourceDir TEMPLATE ========
 */



/*
 * ======== ti.catalog.msp430.init.Boot TEMPLATE ========
 */

    extern Void ti_catalog_msp430_init_Boot_disableWatchdog(UInt address);
    extern Void ti_catalog_msp430_init_Boot_configureDCO(Void);

#if defined(__ti__)
#pragma CODE_SECTION(ti_catalog_msp430_init_Boot_init, ".text:.bootCodeSection")
#endif

/*
 *  ======== ti_catalog_msp430_init_Boot_init ========
 */
#if defined(__ICC430__)
    #pragma location="CSTART"
#endif
Void ti_catalog_msp430_init_Boot_init(Void)
{
}



/*
 * ======== ti.mcu.msp430.csl.CSL TEMPLATE ========
 */

/* CSL stuff */

/*
 * ======== ti.mcu.msp430.csl.adc.ADC10 TEMPLATE ========
 */

/* ADC10 stuff from C:/ti/grace_2_10_00_78/packages/ti/mcu/msp430/csl/adc/./ADC10.xdt */

/*
 * ======== ti.mcu.msp430.csl.clock.BCSplus TEMPLATE ========
 */

/* 2xx Clock stuff from C:/ti/grace_2_10_00_78/packages/ti/mcu/msp430/csl/clock/./BCSplus.xdt */

/*
 * ======== ti.mcu.msp430.csl.system.System TEMPLATE ========
 */

/* System stuff from C:/ti/grace_2_10_00_78/packages/ti/mcu/msp430/csl/system/./System.xdt */

/*
 * ======== ti.mcu.msp430.csl.watchdog.WDTplus TEMPLATE ========
 */

/* WDTplus stuff from C:/ti/grace_2_10_00_78/packages/ti/mcu/msp430/csl/watchdog/./WDTplus.xdt */

/*
 * ======== ti.mcu.msp430.csl.gpio.GPIO TEMPLATE ========
 */

/* GPIO stuff from C:/ti/grace_2_10_00_78/packages/ti/mcu/msp430/csl/gpio/./GPIO.xdt */

/*
 * ======== ti.mcu.msp430.csl.interrupt_vectors.InterruptVectors TEMPLATE ========
 */

/* 5xx Clock stuff from C:/ti/grace_2_10_00_78/packages/ti/mcu/msp430/csl/interrupt_vectors/./InterruptVectors.xdt */

/*
 * ======== PROGRAM GLOBALS ========
 */


/*
 * ======== CONSTANTS ========
 */

