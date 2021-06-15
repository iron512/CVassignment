#!/usr/bin/python

import cv2
import sys
import os
import numpy as np

import utility as ut
import setup

#check if an argument is passed correctly
if len(sys.argv) != 3:
	print("\nError found:",ut.red("Incorrect arguments."),"\nTerminating.\n\nRun using this command:\n\n\t",ut.grn("python3 preprocessor.py <video_file> <debug>\n")	)
	sys.exit(1)

video = sys.argv[1]
debug = int(sys.argv[2])
check, cap = setup.loadCapture(video)

if not check:
	sys.exit(1)

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#save just a frame each 18. For calculating the mode/average is more than enough
frames = setup.splitCapture(cap, 18, debug = debug)
cap.release()
frames_gray = []

for i in range(0,len(frames)):
	gray = cv2.cvtColor(frames[i],cv2.COLOR_RGB2GRAY)
	frames_gray.append(gray)

average_result = np.zeros((height,width))
mode_result = np.zeros((height,width))
old_percentage = -1

for x in range(height):
	for y in range(width):
		pixellist = [None] * len(frames_gray)
		for k in range(len(frames_gray)):
			pixellist[k] = frames_gray[k][x][y]

		average_result[x][y] = np.mean(pixellist)
		mode_result[x][y] = max(pixellist, key=pixellist.count)

	if old_percentage != int((x+1)*100/height):
		old_percentage = int((x+1)*100/height)
		if debug >= 1:
			print("Computation (%):",ut.grn(str(int((x+1)*100/height))+"%"),"\tRAM consumption:",ut.ylw(ut.memory()))

if debug >= 1:
	print("analyzed frames:",len(frames_gray))

if debug == 1:
	cv2.imshow('average', average_result.astype(np.uint8))
cv2.imwrite('./sources/bg_avg.png', average_result.astype(np.uint8))

if debug == 1:
	cv2.imshow('mode', mode_result.astype(np.uint8))
cv2.imwrite('./sources/bg_mode.png', mode_result.astype(np.uint8))

cv2.waitKey(0)

#gentle quit
cv2.destroyAllWindows()