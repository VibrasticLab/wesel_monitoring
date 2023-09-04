/**
 * @file vib_analog.c
 * @brief Analog Reading code
 *
 * @addtogroup Analog
 * @{
 */

#include "vib_includes.h"

static adcsample_t samples[ADC_GRP1_NUM_CHANNELS * ADC_GRP1_BUF_DEPTH];
static uint32_t sum_adc_tps;


void adc_cb(ADCDriver *adcp, adcsample_t *buffer, size_t n){
    (void)adcp;
    (void) buffer;
    (void) n;
    uint8_t i;

    if(adcp->state == ADC_COMPLETE){
        sum_adc_tps = 0;

        for(i=0;i<ADC_GRP1_BUF_DEPTH;i++){
            sum_adc_tps = sum_adc_tps + samples[0 + (i*ADC_GRP1_NUM_CHANNELS)];
        }
    }
}

/** @}*/