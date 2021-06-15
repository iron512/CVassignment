#!/usr/bin/python

import sys
import cv2
import numpy as np

import utility as ut
import setup

#check if an argument is passed
if len(sys.argv) != 3:	
	print("\nError found:",ut.red("Incorrect arguments."),"\nTerminating.\n\nRun using this command:\n\n\t",ut.grn("python3 preprocessor.py <video_file> <debug>\n"))
	sys.exit(1)

video = sys.argv[1]
debug = int(sys.argv[2])
check, cap = setup.loadCapture(video)

if not check:
	sys.exit(1)

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

out_light = cv2.VideoWriter(video.replace(".mp4", "_light.mp4"), fourcc, 25.0, (width,height))
gamma_light = 0.5
out_contrast = cv2.VideoWriter(video.replace(".mp4", "_contrast.mp4"), fourcc, 25.0, (width,height))
gamma_contrast = 1.7

count = 0
while True:
	ret, frame = cap.read()
	if ret:
		if debug == 1:
			cv2.imshow("orginal",frame)
		
		lookUpTable_light = np.empty((1,256), np.uint8)
		lookUpTable_contrast = np.empty((1,256), np.uint8)
		for i in range(256):
			lookUpTable_light[0,i] = np.clip(pow(i / 190.0, gamma_light) * 190.0, 0, 255)
			lookUpTable_contrast[0,i] = np.clip(pow(i / 255.0, gamma_contrast) * 255.0, 0, 255)
		frame_light = cv2.LUT(frame, lookUpTable_light)
		frame_contrast = cv2.LUT(frame, lookUpTable_contrast)

		if debug == 1:
			cv2.imshow("light",frame_light)
			cv2.imshow("contrast",frame_contrast)
		out_light.write(frame_light)
		out_contrast.write(frame_contrast)

		cv2.waitKey(1)		
		count += 1
	else:
		break

cap.release()
out_light.release()
out_contrast.release()

if debug == 1:
	print("Total Frames: " + str(count))

f = open("frames.txt", "w")
f.write(str(count))
f.close()

cv2.destroyAllWindows()