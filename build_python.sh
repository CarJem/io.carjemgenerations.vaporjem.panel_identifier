#!/bin/bash
pyinstaller --onefile \
 --specpath ./code \
 --distpath ./contents/code/ \
 --workpath ./code/ \
 --name panel_updater \
 ./code/main.py