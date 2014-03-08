CC=gcc
PRU_ASM=pasm -V3

all: hcsr04_demo hcsr04_demo.bin

hcsr04_demo: hcsr04_demo.o 
	$(CC) -lpthread -lprussdrv -o hcsr04_demo hcsr04_demo.o

hcsr04_demo.o: hcsr04_demo.c
	$(CC) -c -std=c99 -o hcsr04_demo.o hcsr04_demo.c

hcsr04_demo.bin: hcsr04_demo.p
	$(PRU_ASM) -b hcsr04_demo.p
	
clean:
	rm -rf hcsr04_demo hcsr04_demo.o hcsr04_demo.bin

