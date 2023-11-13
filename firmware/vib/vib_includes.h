/**
 * @file vib_includes.h
 * @brief Global Inclusion header
 *
 * @addtogroup Main
 * @{
 */

#ifndef _VIB_INCLUDES_H_
#define _VIB_INCLUDES_H_

/**
 * @brief Serial using Shell or not for testing purpose
 *
 */
#define VIB_USE_SHELL   FALSE

/**
 * @brief USE USB Serial for Data Stream
 * @details WARNING: ADC Data Burst using USB Serial resulting RTOS/DMA crash
 * @details Should always FALSE
 *
 */
#define VIB_USE_USB     FALSE

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdlib.h>
#include <math.h>

#include "ch.h"
#include "hal.h"

#include "shell.h"
#include "chprintf.h"

#include "vib_serial.h"
#include "vib_analog.h"

#endif

 /** @}*/
