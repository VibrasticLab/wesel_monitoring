/**
 * @file vib_analog.h
 * @brief Analog Reading header
 *
 * @addtogroup Analog
 * @{
 */

#ifndef _VIB_ANALOG_H_
#define _VIB_ANALOG_H_

/**
 * @brief ADC Channel Number
 * @details For now, use only Z
 */
#define ADC_GRP1_NUM_CHANNELS   1

/**
 * @brief Averaging Buffer Depth
 */
#define ADC_GRP1_BUF_DEPTH      10

/**
 * @brief Analog reading initialization
 *
 */
void vib_Analog_Init(void);

#endif

 /** @} */