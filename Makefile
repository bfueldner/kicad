LIBRARY_ROOT = library
FOOTPRINT_ROOT = modules
CSV_ROOT := data/device
TEMPLATE_ROOT := data/template
TABLE_ROOT := data/symbol

COMMON_SCRIPT_DEPS = script/config.py script/symbol.py config
CPU_SCRIPT = script/cpu.py

CAPACITOR_SCRIPT = script/capacitor.py
DEVICE_SCRIPT = script/device.py
FOOTPRINT_SCRIPT = script/footprint.py
SUMMARY_SCRIPT = script/summary.py
README_SCRIPT = script/readme.py
PROJECT_SCRIPT = script/project.py

# Generator based symbols
LIBRARIES = $(LIBRARY_ROOT)/mcu.lib \
			$(LIBRARY_ROOT)/rf.lib \
			$(LIBRARY_ROOT)/capacitor.lib

# Template/table based symbols
TEMPLATE_LIBRARIES := $(LIBRARY_ROOT)/supply.lib \
	$(LIBRARY_ROOT)/led.lib \
	$(LIBRARY_ROOT)/transistor.lib \
	$(LIBRARY_ROOT)/logic.lib \
	$(LIBRARY_ROOT)/diode.lib \
	$(LIBRARY_ROOT)/driver.lib

TEMPLATE_LIBRARIES_CSV := $(patsubst $(LIBRARY_ROOT)/%.lib, $(CSV_ROOT)/%.csv, $(TEMPLATE_LIBRARIES))

# Footprints
FOOTPRINTS = dip \
	soic \
	plcc \
	pqfp \
	sqfp

all: $(FOOTPRINTS) $(LIBRARIES) $(TEMPLATE_LIBRARIES) summary.txt library.pro README.md

MCU_CLOCK = data/mcu/pin-table-TM4C123GH6PM.csv\
			data/mcu/stm32F030C8T6RT.csv

$(LIBRARY_ROOT)/mcu.lib: $(CPU_SCRIPT) $(COMMON_SCRIPT_DEPS) $(MCU_CLOCK)
	$(CPU_SCRIPT) --clock $(MCU_CLOCK) --output $@

RF_CLOCK = data/rf/cc1121.csv data/rf/si4468.csv

$(LIBRARY_ROOT)/rf.lib: $(CPU_SCRIPT) $(COMMON_SCRIPT_DEPS) $(RF_CLOCK)
	$(CPU_SCRIPT) --clock $(RF_CLOCK) --output $@

CAPACITOR = data/avx_condensator.csv

$(LIBRARY_ROOT)/capacitor.lib: $(CAPACITOR_SCRIPT) $(COMMON_SCRIPT_DEPS) $(CAPACITOR)
	$(CAPACITOR_SCRIPT) --data $(CAPACITOR) --output $@

# Template based symbols
$(LIBRARY_ROOT)/%.lib: $(CSV_ROOT)/%.csv $(DEVICE_SCRIPT) $(COMMON_SCRIPT_DEPS)
	$(DEVICE_SCRIPT) --csv $< --symbol $@ --desc $(addsuffix .dcm, $(basename $@)) --template_path $(TEMPLATE_ROOT)/ --table_path $(TABLE_ROOT)/

# Footprint generation
$(FOOTPRINTS): %: data/footprint/%.csv
	mkdir -p $(FOOTPRINT_ROOT)/$@
	$(FOOTPRINT_SCRIPT) --csv $< --output_path $(FOOTPRINT_ROOT)/$@

summary.txt: $(FOOTPRINTS) $(LIBRARIES) $(TEMPLATE_LIBRARIES)
	$(SUMMARY_SCRIPT) --libs $(LIBRARIES) --footprints $(FOOTPRINTS) --output $@

# Uncomment dependency on $(FOOTPRINTS), when it works!
#library.pro: $(FOOTPRINTS) $(LIBRARIES) $(TEMPLATE_LIBRARIES)
library.pro: $(LIBRARIES) $(TEMPLATE_LIBRARIES)
	$(PROJECT_SCRIPT) --template data/project.pro --symbol_path $(LIBRARY_ROOT) --footprint_path $(FOOTPRINT_ROOT) --project $@

README.md: config
	$(README_SCRIPT) --output $@
