obj-m += sc16is7xx_ext.o
sc16is7xx_ext-y := sc16is7xx.o

ccflags-y += -Wno-declaration-after-statement

all:
	$(MAKE) -C $(KERNEL_SRC) O=$(KBUILD_OUTPUT) M=$(PWD) modules

clean:
	$(MAKE) -C $(KERNEL_SRC) O=$(KBUILD_OUTPUT) M=$(PWD) clean
