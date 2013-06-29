# optional compiler flags
CCOPTS ?= --symdebug:dwarf --optimize_with_debug -qq -pdsw225 

# required C preprocessor flags
#    compiler   headers: "C:/ti/ccsv5/tools/compiler/msp430_4.1.5/include"
#    device     headers: "C:/ti/ccsv5/ccs_base/msp430/include"
#    Grace      headers: "C:/ti/grace_2_10_00_78/packages" 
CPPFLAGS = -D__MSP430G2332__ -I "C:/ti/ccsv5/tools/compiler/msp430_4.1.5/include" -I "C:/ti/grace_2_10_00_78/packages"  -I "C:/ti/ccsv5/ccs_base/msp430/include" 

# the compiler and archiver commands
CC = "C:/ti/ccsv5/tools/compiler/msp430_4.1.5/bin/cl430" --abi=eabi -c --obj_directory=objs/  -vmsp
AR = "C:/ti/ccsv5/tools/compiler/msp430_4.1.5/bin/ar430" rq
RM = cmd.exe /q /c del /f
MKDIR = mkdir

# create object sub-directory, if necessary
ifeq (,$(wildcard objs/))
    $(shell $(MKDIR) objs\)
endif

all: grace.lib

# add power advice options to the Grace generated files
objs/Grace_init.obj objs/CSL_init.obj objs/GPIO_init.obj objs/BCSplus_init.obj objs/ADC10_init.obj objs/InterruptVectors_init.obj objs/System_init.obj objs/WDTplus_init.obj: CCOPTS := $(CCOPTS) --advice:power=all
    
# pattern rule to compile .c source to an object file
objs/%.obj: %.c makefile
	@echo cle430 $< ...
	$(CC) $(CCOPTS) $(CPPFLAGS) "$<"

# rule to combine all objects into the grace.lib library
grace.lib: objs/Grace_init.obj objs/CSL_init.obj objs/GPIO_init.obj objs/BCSplus_init.obj objs/ADC10_init.obj objs/InterruptVectors_init.obj objs/System_init.obj objs/WDTplus_init.obj
	@ echo are430 $@ $< ...
	$(AR) $@ $^

# clean removes all generated files 
clean:
	-$(RM) grace.lib
	-$(RM) "objs\"*.obj

