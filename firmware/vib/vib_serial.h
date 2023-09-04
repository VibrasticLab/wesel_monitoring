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

#endif

/** @} */