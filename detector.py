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

kernel4 = np.ones((4,4),np.uint8)
kernel6 = np.ones((6,6),np.uint8)
kernelre = np.ones((9,3),np.uint8)

billboard_back = cv2.dilate(cv2.erode(imgblack - imgwhite, kernel4),kernel6)
billboard_back = np.uint8(255-billboard_back)

if not check:
	sys.exit(1)

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

i = 0
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("./output/detector.mp4", fourcc, 25.0, (width,height))

while True:
	ret, frame = cap.read()
	if ret:
		frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)    

		back_sub = cv2.absdiff(average_back, frame_gray)
		ret3, back_sub_threshold = cv2.threshold(back_sub,60,255,cv2.THRESH_BINARY) 

		if debug == 1:
			cv2.imshow('back_sub',back_sub_threshold)
	
		back_bil = np.bitwise_and(billboard_back,back_sub_threshold)
		back_bil = cv2.dilate(back_bil,kernelre)
		
		if debug == 1:
			cv2.imshow('back_bil',back_bil)

		contours,hierarchy = cv2.findContours(back_bil, 1, 2)

		ppl = 0;
		for cnt in contours:
			x,y,w,h = cv2.boundingRect(cnt)
			
			if w*h > 970 and w*1.2<h:
				color = (255,255,255)
				cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
				ppl+=1
			elif w*h > 970 and w<h:
				color = (127,127,127)	
				cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
				ppl+=1		

		cv2.putText(frame,'People detected: '+str(ppl) ,(10,130), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2)


		out.write(frame)
		if debug >= 1:
			cv2.imshow("boxed",frame)

		cv2.waitKey(1)		
		i=i+1
	else:
		break

out.release()
cap.release()
cv2.destroyAllWindows()