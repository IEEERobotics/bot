# invoke SourceDir generated makefile for main.pe430
main.pe430: .libraries,main.pe430
.libraries,main.pe430: package/cfg/main_pe430.xdl
	$(MAKE) -f C:\Users\Neal\Dropbox\IR_Array\MSP430~1\g2332_grace_adc_push_demo/src/makefile.libs

clean::
	$(MAKE) -f C:\Users\Neal\Dropbox\IR_Array\MSP430~1\g2332_grace_adc_push_demo/src/makefile.libs clean

