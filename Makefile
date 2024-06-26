all: build

.PHONY: build client server

CC = gcc
DATE := $(shell date "+%Y-%m-%d")
COMPILE_FLAGS = -Og -g -ggdb3 -march=native -mtune=native -Wall -D_FORTIFY_SOURCE=2 -fmodulo-sched -Wno-format-overflow
# COMPILE_FLAGS = -Ofast -ggdb3 -march=native -mtune=native -Wall -D_FORTIFY_SOURCE=2 -fmodulo-sched
INCLUDE_FLAGS = 
LIBRARY_FLAGS = -lncursesw -lpanelw
 DEFINE_FLAGS = -D_DEFAULT_SOURCE -D_XOPEN_SOURCE=600
PWD := $(shell pwd)
MANPREFIX = /usr/share/man

build:
	$(CC) $(COMPILE_FLAGS) $(DEFINE_FLAGS) $(LIBRARY_FLAGS) -o resources/ankeec ankeec.c

install: build
	cp resources/ankeec /usr/local/bin/ankeec
	cp resources/sankee /usr/local/bin/sankee
	mkdir -p /usr/share/ankee/
	ln -fs $(PWD)/resources/JMdict_e.xml /usr/share/ankee/JMdict_e.xml
	ln -fs $(PWD)/ankeed /usr/local/bin/ankeed
	cp ankee.1 $(MANPREFIX)/man1/ankee.1
	chmod 644 $(MANPREFIX)/man1/ankee.1
	@echo '	Add'
	@echo '		if [ "$$ANKEEC" = "1" ]'
	@echo '				exec ankeec "$$(cat /tmp/ankeect)" "$$(cat /tmp/ankeecp)"'
	@echo '		end'
	@echo '	to ~/.config/fish/config.fish'

STRING = "ab cd()\ のこ“人間“泣けばゼミ…き命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題"
# STRING = "のこ人間泣けばゼミき命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題命題"
# STRING = "ab cd()\ のこ人間泣けばゼミ/き"
run: build
	./resources/ankeec $(STRING) "/tmp/mata"

debug: build
	gdb -q --args ./resources/ankeec $(STRING) "/tmp/mata"
