#!/usr/bin/python

from pathlib import Path

import cv2
import sys
import os
import numpy as np

import utility as ut

#This file contains 3 function, for preparing the video to further processes.
#In the end, just two will be used, b

#LOADCAPTURE: verifies the integrity of the video passed as parameter, 
#opening and returning the videocapture object (if the operation was successful)
def loadCapture(videopath):
	#check if the argument passed exist as file
	if not os.path.exists(videopath):
		print("\nError found:", ut.red("invalid file."), "\nTerminating.\n\nArgument passed ("+ ut.ylw(videopath) +") is not a valid file.\n")
		return False, None

	#check if the argument passed is a valid video
	cap = cv2.VideoCapture(videopath)
	if not cap.isOpened():
		print("Error found:",ut.red("wrongly formatted file (Not a video)."), "\nTerminating.\n\nCheck again the file passed ("+ ut.ylw(videopath)+").\n")
		return False, None

	return True, cap

#SPLITCAPTURE: Waiting each time for the video to be loaded can be tedious as
#the framerate is costant. The video gets splitted and saved as images, in order to
#allow the loading of just these.
def splitCapture(capture, step = 1, write = False, debug = True, waiting_time = 1):
	if write:
		Path("./images").mkdir(parents=True, exist_ok=True)
	video = []

	i = 0
	while True:
		ret, frame = capture.read()
		if ret:
			if i % step == 0:
				video.append(frame)
			if debug == 1:
				cv2.imshow('frame', frame)
			if write:
				cv2.imwrite("./images/colored"+str(i)+".png", frame)
			cv2.waitKey(waiting_time)

			i=i+1
		else:
			break

	return video

#LOADIMAGES: Once split, the video must be loaded back into memory. 
#I honestly thought this step would reduce a lot the loading phase,
#but turns out that it is still worth to load the video completely
def loadImages():
	qt = len([name for name in os.listdir('./images/')])
	
	video = [None] * qt
	old_percentage = -1
	for i in range(qt):
		frame = cv2.imread("./images/colored"+str(i)+".png",1)
		video[i] = frame
		if old_percentage != int((i+1)*100/qt):
			old_percentage = int((i+1)*100/qt)
			print("Images loaded:", ut.grn(str(old_percentage) + "%"))

	return video
