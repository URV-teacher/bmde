#---------------------------------------------------------------------------------
# Makefile of the course that runs make, make run and make debug in the Docker images of the BMDE, with compose
#
# Copy it to the root of your NDS project instead of its Makefile, with the compose.yml next to it: the only requirement
# of the computer is then Docker. In the host, each target runs the service of compose.yml of its component: the build
# (and any other target, e.g. make clean) in build, run in desmume and debug in desmume and insight. Edit compose.yml to
# change how they run, or to extend their images with a Dockerfile.
#
# Inside the containers (DOCKER_FLAG, which they get from here), or when the tools are installed (DEVKITARM, e.g. in a
# host with scripts/install.sh of bmde, or in the shell of aleixmt/bmde-full), it is the Makefile of the course as is
# (examples/Makefile of bmde), from the else below. git and the VPN are not covered: use git and connect_vpn.sh of the
# host, or bmde git.
#---------------------------------------------------------------------------------
ifeq ($(strip $(DOCKER_FLAG)$(DEVKITARM)),)
#---------------------------------------------------------------------------------
# In the host: each target in the container of its component
#---------------------------------------------------------------------------------
# Tag of the images (e.g. 1.14.0, to pin a version of the BMDE)
BMDE_TAG	?=	latest
# The ROM is named after the folder of the project, as in the Makefile of the course
TARGET		:=	$(notdir $(CURDIR))
# Port of the GDB stub of the emulator, the one of the Makefile of the course
DEBUG_PORT	:=	1000
# compose.yml, next to this Makefile, has a service for each component (build, desmume, insight). The project is
# mounted at /input/$(TARGET) in them, and the files created by the build are owned by the user of the host
COMPOSE		:=	PROJECT=$(TARGET) BMDE_UID=$(shell id -u) BMDE_GID=$(shell id -g) BMDE_TAG=$(BMDE_TAG) \
				docker compose -f $(CURDIR)/compose.yml
# The debugger reaches the emulator by its name, in the network of the project of compose
EMULATOR_NAME	:=	bmde-desmume-$(TARGET)

.DEFAULT_GOAL	:=	build
.PHONY: build run debug

#---------------------------------------------------------------------------------
build:
	@$(COMPOSE) run --rm build

#---------------------------------------------------------------------------------
run: build
	@echo "runing $(TARGET).nds with DesmuME (stop it with: docker stop $(EMULATOR_NAME))"
	@docker rm -f $(EMULATOR_NAME) > /dev/null 2>&1 || true
	@$(COMPOSE) run --rm -d --name $(EMULATOR_NAME) desmume /roms/$(TARGET).nds > /dev/null

#---------------------------------------------------------------------------------
# The emulator is stopped when the debugger is closed
debug: build
	@echo "testing $(TARGET).nds/.elf with DeSmuME_dev/Insight (gdb) through TCP port=$(DEBUG_PORT)"
	@docker rm -f $(EMULATOR_NAME) > /dev/null 2>&1 || true
	@$(COMPOSE) run --rm -d --name $(EMULATOR_NAME) desmume --arm9gdb=$(DEBUG_PORT) /roms/$(TARGET).nds > /dev/null
	@GDB_TARGET=$(EMULATOR_NAME):$(DEBUG_PORT) $(COMPOSE) run --rm insight $(TARGET).elf; \
	status=$$?; docker stop $(EMULATOR_NAME) > /dev/null; exit $$status

#---------------------------------------------------------------------------------
# Any other target (e.g. clean, or a file) is made by the Makefile of the course in the container of devkitARM. The
# Makefile itself is not remade
Makefile: ;
%:
	@$(COMPOSE) run --rm build $@

#---------------------------------------------------------------------------------
else
#---------------------------------------------------------------------------------
# In the containers, or with the tools installed: the Makefile of the course
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
.SUFFIXES:
#---------------------------------------------------------------------------------

ifeq ($(strip $(DEVKITARM)),)
$(error "Please set DEVKITARM in your environment. export DEVKITARM=<path to>devkitARM")
endif

ifeq ($(strip $(DEVKITPRO)),)
$(error "Please set DEVKITPRO in your environment. export DEVKITPRO=<path to>devkitPRO")
endif

ifeq ($(strip $(DESMUME)),)
$(error "Please set DESMUME in your environment. export DESMUME=<path to>DeSmuME")
endif

include $(DEVKITARM)/ds_rules

#---------------------------------------------------------------------------------
# TARGET is the name of the output
# BUILD is the directory where object files & intermediate files will be placed
# SOURCES is a list of directories containing source code
# INCLUDES is a list of directories containing extra header files
# DATA contains .bin files with extra data for the project (e.g. graphic tiles)
#---------------------------------------------------------------------------------
TARGET		:=	$(shell basename $(CURDIR))
BUILD		:=	build
SOURCES		:=	source
INCLUDES	:=	include
DATA		:=	data

#---------------------------------------------------------------------------------
# options for code generation
#---------------------------------------------------------------------------------
ARCH	:=	 -march=armv5te -mlittle-endian

CFLAGS	:=	-Wall -gdwarf-3 -O2 \
			$(ARCH) -mtune=arm946e-s -fomit-frame-pointer -ffast-math
				# -Wall						: enable all warnings
				# -gdwarf-3					: enable debug info generation (v3)
				# -O2						: code optimization level 2
				# $(ARCH) -mtune=arm946e-s	: tune code generation for specific machine
				# -fomit-frame-pointer 		: avoid to use a 'frame-pointer' register in functions that do not need it
				# -ffast-math				: optimize math operations

CFLAGS	+=	$(INCLUDE) -DARM9

ASFLAGS	:=	$(INCLUDE) -g $(ARCH)
LDFLAGS	=	-specs=ds_arm9.specs $(ARCH)

#---------------------------------------------------------------------------------
# any extra libraries we wish to link with the project
#---------------------------------------------------------------------------------
LIBS	:= -lnds9

#---------------------------------------------------------------------------------
# list of directories containing libraries, this must be the top level containing
# include and lib
#---------------------------------------------------------------------------------
LIBDIRS	:=	$(LIBNDS)

#---------------------------------------------------------------------------------
# no real need to edit anything past this point unless you need to add additional
# rules for different file extensions
#---------------------------------------------------------------------------------
ifneq ($(BUILD),$(notdir $(CURDIR)))
#---------------------------------------------------------------------------------

export OUTPUT	:=	$(CURDIR)/$(TARGET)

export VPATH	:=	$(foreach dir,$(SOURCES),$(CURDIR)/$(dir))
export DEPSDIR	:=	$(CURDIR)/$(BUILD)

CFILES		:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.c)))
SFILES		:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.s)))
BINFILES	:=	$(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.bin)))

export OFILES	:=	$(BINFILES:.bin=.o) $(CFILES:.c=.o) $(SFILES:.s=.o)

export INCLUDE	:=	$(foreach dir,$(INCLUDES),-I$(CURDIR)/$(dir)) \
					$(foreach dir,$(LIBDIRS),-I$(dir)/include)

export LIBPATHS	:=	$(foreach dir,$(LIBDIRS),-L$(dir)/lib)

#---------------------------------------------------------------------------------
# use CC for linking standard C projects
#---------------------------------------------------------------------------------
export LD	:=	$(CC)

export GAME_TITLE	:=	CANDYNDS
export GAME_SUBTITLE1	:=	Practica de Computadores
export GAME_SUBTITLE2	:=	Grado de Ingenieria Informatica (URV)
export GAME_ICON	:= 	$(DEVKITPRO)/libnds/icon.bmp


.PHONY: $(BUILD) clean

#---------------------------------------------------------------------------------
$(BUILD):
	@[ -d $@ ] || mkdir -p $@
	@make --no-print-directory -C $(BUILD) -f $(CURDIR)/Makefile

#---------------------------------------------------------------------------------
clean:
	@echo "Removing ALL intermediate files... "
	@echo "Por favor, recuerda que habitualmente NO es necesario hacer un 'clean' antes de un 'make'"
	@sleep 3
	@rm -fr $(BUILD) $(TARGET).elf $(TARGET).nds

#---------------------------------------------------------------------------------
run : $(TARGET).nds
	@echo "runing $(TARGET).nds with DesmuME"
	@$(DESMUME)/DeSmuME_dev.exe $(TARGET).nds &

#---------------------------------------------------------------------------------
debug : $(TARGET).nds $(TARGET).elf
	@echo "testing $(TARGET).nds/.elf with DeSmuME_dev/Insight (gdb) through TCP port=1000"
	@$(DESMUME)/DeSmuME_dev.exe --arm9gdb=1000 $(TARGET).nds &
	@$(DEVKITPRO)/insight/bin/arm-eabi-insight $(TARGET).elf &

#---------------------------------------------------------------------------------
else

DEPENDS	:=	$(OFILES:.o=.d)

#---------------------------------------------------------------------------------
# main targets
#---------------------------------------------------------------------------------
$(OUTPUT).nds	: 	$(OUTPUT).elf
$(OUTPUT).elf	:	$(OFILES)

#---------------------------------------------------------------------------------
%.o	:	%.bin
#---------------------------------------------------------------------------------
	@echo $(notdir $<)
	$(bin2o)


-include $(DEPENDS)

#---------------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------
