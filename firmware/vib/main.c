/**
 * @file main.c
 * @brief Main Entry code
 *
 * @addtogroup Main
 * @{
 */

#include "vib_includes.h"

/*
 * Red LED blinker thread, times are in milliseconds.
 */
static THD_WORKING_AREA(waThread1, 128);
static THD_FUNCTION(Thread1, arg) {

  (void)arg;
  chRegSetThreadName("blinker");
  while (true) {
    palClearPad(GPIOB, 6);
    chThdSleepMilliseconds(500);
    palSetPad(GPIOB, 6);
    chThdSleepMilliseconds(500);
  }
}

/*
 * Application entry point.
 */
int main(void) {

  halInit();
  chSysInit();

  vib_Serial_Init();
  vib_Analog_Init();

  /*
   * Creates the blinker thread.
   */
  palSetPadMode(GPIOB, 6, PAL_MODE_OUTPUT_PUSHPULL);
  chThdCreateStatic(waThread1, sizeof(waThread1), NORMALPRIO, Thread1, NULL);

  while (true) {
    vib_Serial_Loop();
    chThdSleepMilliseconds(500);
  }
}

/** @}*/
