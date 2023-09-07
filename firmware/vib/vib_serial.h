/**
 * @file vib_serial.h
 * @brief Serial Interface header
 *
 * @addtogroup Interface
 * @{
 */

#ifndef _VIB_SERIAL_H_
#define _VIB_SERIAL_H_

#define SHELL_WA_SIZE   THD_WORKING_AREA_SIZE(2048)
#define TEST_WA_SIZE    THD_WORKING_AREA_SIZE(256)

#define vib_Shell_Init()    shellInit()

/******************** USB PART *****************/

#define USBD1_DATA_REQUEST_EP           1
#define USBD1_DATA_AVAILABLE_EP         1
#define USBD1_INTERRUPT_REQUEST_EP      2

/***********************************************/

/**
 * @brief Serial and Shell Initialization
 *
 */
void vib_Serial_Init(void);

/**
 * @brief Shell Looping
 *
 */
void vib_Serial_Loop(void);

/**
 * @brief USB Serial Initialization
 *
 */
void vib_USBSerial_Init(void);

/**
 * @brief USB Looping
 *
 */
void vib_USBSerial_Loop(void);

#endif

/** @} */
