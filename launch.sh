#!/bin/bash
VIDEO="CV_basket.mp4"
VID_PATH="./sources/${VIDEO}"

if [[ -d "virtual" ]]; then
	echo "running detection in background"
	. virtual/bin/activate
	python3 detector.py "${VID_PATH//".mp4"}_contrast.mp4" "./sources/bg_avg.png" "./sources/bg_mode.png" 2 &
	deactivate
fi

if [[ -d "./tracking/CMakeFiles" ]]; then
	echo "running tracking in background"
	cd "./tracking"
	./track ".${VID_PATH//".mp4"}_light.mp4" 2 &
	cd ..
fi

if [[ -d "./ball_possession/CMakeFiles" ]]; then
	echo "running ball possession in background"
	cd "./ball_possession"
	./ball_poss ".${VID_PATH//".mp4"}_contrast.mp4" "../sources/bg_mode.png" 2 &
	cd ..
fi