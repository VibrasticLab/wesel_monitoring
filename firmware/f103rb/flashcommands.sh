#!/bin/bash

st-flash --connect-under-reset --reset --format ihex write build/ch.hex

