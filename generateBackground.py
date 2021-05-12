#!/usr/bin/python

import cv2
import sys
import os
import numpy as np

import utility as ut
import setup

#check if an argument is passed
if len(sys.argv) != 2:	
	print("\nError found:",ut.red("Incorrect arguments."),"\nTerminating.\n\nRun using this command:\n\n\t",ut.grn("python3 main.py <video_file>\n"))
	sys.exit(1)

video = sys.argv[1]
check, cap = setup.loadCapture(video)

if not check:
	sys.exit(1)

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#save just a frame each 20. For calculating the mode/average is enough
frames = setup.splitCapture(cap, 20)
cap.release()
frames_gray = []

for i in range(0,len(frames)):
	gray = cv2.cvtColor(frames[i],cv2.COLOR_RGB2GRAY)
	frames_gray.append(gray)

#average_result = np.zeros((height,width))
mode_result = np.zeros((height,width))
old_percentage = -1

for x in range(height):
	for y in range(width):
		mode_test = [None] * len(frames_gray)
		#average_test = 0
		for k in range(len(frames_gray)):
			#average_test = average_test + frames_gray[k][x][y]
			mode_test[k] = frames_gray[k][x][y]

		#average_result[x][y] = int(average_test/len(frames_gray))
		mode_result[x][y] = max(mode_test, key=mode_test.count)

	if old_percentage != int((x+1)*100/height):
		old_percentage = int((x+1)*100/height)
		print("Computation (%):",ut.grn(str(int((x+1)*100/height))+"%"),"\tRAM consumption:",ut.ylw(ut.memory()))

print("analyzed frames:",len(frames_gray))

#cv2.imshow('average', average_result.astype(np.uint8))
#cv2.imwrite('average.png', average_result.astype(np.uint8))
cv2.imshow('mode', mode_result.astype(np.uint8))
cv2.imwrite('background.png', mode_result.astype(np.uint8))

cv2.waitKey(0)

#gentle quit
cv2.destroyAllWindows()