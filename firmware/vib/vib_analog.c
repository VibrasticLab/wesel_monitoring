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
static adcsample_t adc_z;

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

        adc_z = sum_adc_tps/10;
        chprintf((BaseSequentialStream*)&SD1,"%i\r\n",adc_z);
    }
}

static const ADCConversionGroup adcgrpcfg = {
    FALSE,
    ADC_GRP1_NUM_CHANNELS,
    adc_cb,
    NULL,
    /* HW Dependent Part */
    0,
    0,
    ADC_SMPR2_SMP_AN0(ADC_SAMPLE_239P5),
    0,
    ADC_SQR1_NUM_CH(ADC_GRP1_NUM_CHANNELS),
    0,
    ADC_SQR3_SQ1_N(ADC_CHANNEL_IN0)
};

static THD_WORKING_AREA(wa_adcThread, 128);
static THD_FUNCTION(adcThread, arg) {
  (void)arg;
  while (TRUE) {
    chThdSleepMilliseconds(10);
    adcStartConversion(&ADCD1, &adcgrpcfg, samples, ADC_GRP1_BUF_DEPTH);
  }
}

void vib_Analog_Init(void){
    palSetPadMode(GPIOA, 0, PAL_MODE_INPUT_ANALOG);

    adcStart(&ADCD1, NULL);
    chThdCreateStatic(wa_adcThread, sizeof(wa_adcThread), NORMALPRIO, adcThread, NULL);
}


/** @}*/