.PHONY: all unicode schmoji clean

all: unicode schmoji

unicode:
	python3 scripts/rename_files.py

schmoji:
	python3 scripts/copy_schmoji.py

clean:
	rm -rf unicode schmoji