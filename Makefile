# Project specific
project 		:= White2Chs
rom_code 		:= White2Eng

# Directory configuration.
build_dir 		 = build
game_base       := $(build_dir)/$(rom_code)

exefs 	        := $(game_base)/exefs
romfs 	        := $(game_base)/romfs

knarc			:= tools/knarc/knarc
ndstool   		:= tools/ndstool
armips			:= tools/armips.exe
python			:= python3

# mkdata tools
# TODO: Condense into mkdata & invoke.
genmsg			:= $(python) tools/gen5text.py

include narc.mk

.PHONY: all clean dump

# ROM build.
all: $(knarc) $(ARCS)
	@ mkdir -p $(exefs)
	@ mkdir -p $(romfs)
	@ mkdir -p $(build_dir)/data
	@ echo "[+] Extracting game to $(game_base)..."
	@ $(ndstool) -x $(rom_code).nds -9 $(exefs)/ARM9.bin -7 $(exefs)/ARM7.bin -9i $(exefs)/ARM9i.bin -7i $(exefs)/ARM7i.bin -y9 $(exefs)/ARM9OVT.bin -y7 $(exefs)/ARM7OVT.bin -d $(romfs) -y $(exefs)/overlay -t $(exefs)/banner.bin -h $(exefs)/header.bin
	
	@ echo "[+] Copying build NARCs..."

	$(knarc) -p $(TEXT_SYSTEM_ARC) -d $(build_dir)/text/system
	cp build/data/system.narc $(romfs)/a/0/0/2

	$(knarc) -p $(TEXT_STORY_ARC) -d $(build_dir)/text/story
	cp build/data/story.narc $(romfs)/a/0/0/3

	cp font.narc $(romfs)/a/0/2/3
	@ echo "[+] Making $@..."

	$(ndstool) -c $(project).nds -9 $(exefs)/ARM9.bin -7 $(exefs)/ARM7.bin -9i $(exefs)/ARM9i.bin -7i $(exefs)/ARM7i.bin -y9 $(exefs)/ARM9OVT.bin -y7 $(exefs)/ARM7OVT.bin -d $(romfs) -y $(exefs)/overlay -t $(exefs)/banner.bin -h $(exefs)/header.bin

dump:
	$(knarc) -u $(romfs)/a/0/0/3 -d $(build_dir)/text/story
	$(knarc) -u $(romfs)/a/0/0/2 -d $(build_dir)/text/system

# Tool building.
$(knarc) : $(wildcard tools/knarc)
	@ echo [+] Building knarc...
	@ make --silent -C tools/knarc

# Cleanup.
clean: 
	rm -rf $(project).nds
	rm -rf $(build_dir)
	rm -rf $(knarc)