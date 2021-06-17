#!/usr/bin/python

import cv2
import sys
import os
import numpy as np

import utility as ut
import setup

#check if an argument is passed
if len(sys.argv) != 5:	
	print("\nError found:",ut.red("Incorrect arguments."),"\nTerminating.\n\nRun using this command:\n\n\t",ut.grn("python3 pipeline.py <video_file> <average> <mode> <debug>\n"))
	sys.exit(1)

video = sys.argv[1]
avg = sys.argv[2]
mode = sys.argv[3]
debug = int(sys.argv[4])

check, cap = setup.loadCapture(video)
average_back = cv2.imread(avg,cv2.IMREAD_GRAYSCALE)
mode_back = cv2.imread(mode,cv2.IMREAD_GRAYSCALE)
subtraction_back = np.abs(average_back - mode_back)

ret1, imgblack = cv2.threshold(subtraction_back, 30, 255, cv2.THRESH_BINARY)
ret2, imgwhite = cv2.threshold(subtraction_back, 220, 255, cv2.THRESH_BINARY)

kernel2 = np.ones((2,2),np.uint8)
kernel3Cross = np.ones((3,3),np.uint8)

kernel3Cross[0][0] = 0
kernel3Cross[2][0] = 0
kernel3Cross[0][2] = 0
kernel3Cross[2][2] = 0

kernel4 = np.ones((4,4),np.uint8)
kernel6 = np.ones((6,6),np.uint8)
kernel8 = np.ones((8,8),np.uint8)

billboard_back = cv2.dilate(cv2.erode(imgblack - imgwhite, kernel4),kernel6)
billboard_back = np.uint8(255-billboard_back)

if not check:
	sys.exit(1)

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

i = 0
past = []

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("./output/detector.mp4", fourcc, 25.0, (width,height))

while True:
	ret, frame = cap.read()
	if ret:
		frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)    
		past.append(frame_gray)
		foreground25 = []

		back_sub = cv2.absdiff(average_back, frame_gray)
		ret3, back_sub_threshold = cv2.threshold(back_sub,25,255,cv2.THRESH_BINARY) 
		#back_sub_threshold = cv2.erode(back_sub_threshold,kernel2)
		#back_sub_threshold = cv2.dilate(back_sub_threshold,kernel3Cross)
		
		if debug == 1:
			cv2.imshow('back_sub',back_sub_threshold)
	
		if i>25:
			foreground25 = past.pop(0)

			fore25_sub = cv2.absdiff(foreground25, frame_gray)
			ret4, fore25_sub_threshold = cv2.threshold(fore25_sub,30,255,cv2.THRESH_BINARY) 			

			#fore25_sub_threshold = cv2.erode(fore25_sub_threshold,kernel2)
			#
			fore25_sub_threshold = cv2.dilate(fore25_sub_threshold,kernel4)

			if debug == 1:
				cv2.imshow('foreground_combo',fore25_sub_threshold)

			back_bil = np.bitwise_and(billboard_back,back_sub_threshold)
			if debug == 1:
				cv2.imshow('back_bil',back_bil)


			contours,hierarchy = cv2.findContours(back_bil, 1, 2)
			
			first = False
			for cnt in contours:
				x,y,w,h = cv2.boundingRect(cnt)
				
				if w*h > 1200:
					if first:
						first = False
						color = (0,0,255)
					else:
						color = (0,255,0)
		
					cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)

		out.write(frame)
		if debug >= 2:
			cv2.imshow("boxed",frame)

		cv2.waitKey(1)		
		i=i+1
	else:
		break

out.release()
cap.release()
cv2.destroyAllWindows()