
/*
 *  ======== CSL_init.c ========
 *  DO NOT MODIFY THIS FILE - CHANGES WILL BE OVERWRITTEN
 */

/* header file declaring the Grace master peripheral initialization function */
#include <ti/mcu/msp430/Grace.h>

/*
 *  ======== CSL_init =========
 *  Initialize all configured CSL peripherals.
 *  
 *  This function is DEPRECATED and will be removed from a future version
 *  of Grace. Instead, update your code to use #include <ti/mcu/msp430/Grace.h>
 *  and call Grace_init() directly to apply the Grace-generated peripheral
 *  configuration.
 */
void CSL_init(void)
{
    /* Call the Grace master peripheral initialization function */
    Grace_init();
}
