################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Each subdirectory must supply rules for building sources it contributes
msp430g2xx2_ta_01.obj: ../msp430g2xx2_ta_01.c $(GEN_OPTS) $(GEN_SRCS)
	@echo 'Building file: $<'
	@echo 'Invoking: MSP430 Compiler'
	"C:/TI/ccsv5/tools/compiler/msp430_4.1.2/bin/cl430" -vmsp --abi=eabi -g --include_path="C:/TI/ccsv5/ccs_base/msp430/include" --include_path="C:/TI/ccsv5/tools/compiler/msp430_4.1.2/include" --advice:power=all --define=__MSP430G2332__ --diag_warning=225 --display_error_number --diag_wrap=off --printf_support=minimal --preproc_with_compile --preproc_dependency="msp430g2xx2_ta_01.pp" $(GEN_OPTS__FLAG) "$<"
	@echo 'Finished building: $<'
	@echo ' '


