#!/bin/bash
mkdir -p output
VIDEO="CV_basket.mp4"
VID_PATH="./sources/${VIDEO}"

if ! [[ -d "virtual" ]]; then
	python3 -m venv virtual
	. virtual/bin/activate
	pip install -r requirements.txt
	deactivate
fi

if ! [[ -d "./tracking/CMakeFiles" ]]; then
	cd "./tracking"
	cmake .
	make
	cd ..
fi

if ! [[ -d "./ball_possession/CMakeFiles" ]]; then
	cd "./ball_possession"
	cmake .
	make 
	cd ..
fi

if [[ -d "virtual" ]]; then
	. virtual/bin/activate
	echo "running preprocessor. enhancing video..."
	python3 preprocessor.py $VID_PATH 0 
	echo "running background generator..."
	python3 generate_background.py "${VID_PATH//".mp4"}_contrast.mp4" 2
	echo "done"
	deactivate
fi
