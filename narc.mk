# -------------------------------------------------------------------
# ARC Definitions
# -------------------------------------------------------------------
TEXT_SYSTEM_ARC_INDEX		:= $(romfs)/a/0/0/2
TEXT_SYSTEM_ARC				:= $(build_dir)/data/system.narc

TEXT_STORY_ARC_INDEX		:= $(romfs)/a/0/0/3
TEXT_STORY_ARC				:= $(build_dir)/data/story.narc

TEXT_STORY_FILES := $(wildcard text/story/*.json)
TEXT_STORY_FILE_OBJS := $(patsubst text/story/%.json,$(build_dir)/text/story/%.bin,$(TEXT_STORY_FILES))

TEXT_SYSTEM_FILES := $(wildcard text/system/*.json)
TEXT_SYSTEM_FILE_OBJS := $(patsubst text/system/%.json,$(build_dir)/text/system/%.bin,$(TEXT_SYSTEM_FILES))
# -------------------------------------------------------------------
# Targets 
# -------------------------------------------------------------------
$(build_dir)/text/%.bin : text/%.json
	@ mkdir -p $(@D)
	$(genmsg) -g $< $@

ARCS := $(TEXT_STORY_FILE_OBJS) $(TEXT_SYSTEM_FILE_OBJS)