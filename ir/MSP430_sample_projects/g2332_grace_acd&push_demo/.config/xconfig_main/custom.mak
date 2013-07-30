## THIS IS A GENERATED FILE -- DO NOT EDIT
.configuro: .libraries,e430 linker.cmd package/cfg/main_pe430.oe430

linker.cmd: package/cfg/main_pe430.xdl
	$(SED) 's"^\"\(package/cfg/main_pe430cfg.cmd\)\"$""\"C:/Users/Neal/Dropbox/IR_Array/MSP430 sample project files/g2332_grace_acd&push_demo/.config/xconfig_main/\1\""' package/cfg/main_pe430.xdl > $@
