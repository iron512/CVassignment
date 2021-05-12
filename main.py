#!/usr/bin/python

import cv2
import sys
import os
import numpy as np

#format better the output in the terminal
class bcolors:
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	RESET = '\033[0m'

#check if an argument is passed
if len(sys.argv) != 3:	
	print("\nError found:" + bcolors.RED + " Incorrect arguments. " + bcolors.RESET + "\nTerminating.\n\nRun using this command:\n\n\t" + bcolors.GREEN + "python3 main.py <video_file> <type>\n" + bcolors.RESET)
	sys.exit(1)

#check if the argument passed exist as file
video = sys.argv[1]
typeof = sys.argv[2]

if not os.path.exists(video):
	print("\nError found:" + bcolors.RED + " invalid file. " + bcolors.RESET + "\nTerminating.\n\nArgument passed ("+ bcolors.YELLOW + video + bcolors.RESET +") is not a valid file.\n")
	sys.exit(2)

if typeof != "mode" and typeof != "average":
	print("\nError found:" + bcolors.RED + " invalid type. " + bcolors.RESET + "\nTerminating.\n\nArgument passed ("+ bcolors.YELLOW + typeof + bcolors.RESET +") is not a valid type.\nUse" + bcolors.YELLOW + "average" + bcolors.RESET + " or " + bcolors.YELLOW + "mode" + bcolors.RESET + " instead.")
	sys.exit(2)	

#check if the argument passed is a valid video
cap = cv2.VideoCapture(video)
if not cap.isOpened():
	print("Error found:" + bcolors.RED + " wrongly formatted file (Not a video). " + bcolors.RESET + "\nTerminating.\n\nCheck again the file passed. ("+ bcolors.YELLOW + video + bcolors.RESET +").\n")
	sys.exit(3)

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # float `width`
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`

frames_gray = []
i = 0

while True:
	ret, frame = cap.read()
	if ret:
		gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
		if i % 20 == 0:
			frames_gray.append(gray)

		cv2.imshow('frame',frame)
		cv2.imshow('gray',gray)
		cv2.waitKey(1)

		i=i+1
	else:
		break

#if typeof == "mode":
#average_test = np.zeros((height,width))
mode_test = np.zeros((height,width),dtype=object)
mode_result = np.zeros((height,width))
old_percentage = -1

for x in range(height):
	for y in range(width):
		count = 0
		mode_test[x][y] = []
		for k in range(len(frames_gray)):
			#average_test[x][y] = average_test[x][y] + frames_gray[k][x][y]
			mode_test[x][y].append(frames_gray[k][x][y])
			count = count+1			

	if old_percentage != int((x+1)*100/height):
		old_percentage = int((x+1)*100/height)
		print("Structure filling (%):",bcolors.YELLOW,int((x+1)*100/height),"\b%", bcolors.RESET)

old_percentage = -1
for x in range(height):
	for y in range(width):
		#average_test[x][y] = average_test[x][y]/count
		mode_result[x][y] = max(mode_test[x][y], key=mode_test[x][y].count)

	if old_percentage != int((x+1)*100/height):
		old_percentage = int((x+1)*100/height)
		print("Avg and mode computation (%):",bcolors.GREEN,int((x+1)*100/height),"\b%", bcolors.RESET)


print("analyzed frames:",count)

#cv2.imshow('average', average_test.astype(np.uint8))
cv2.imshow('moded', mode_result.astype(np.uint8))
#cv2.imwrite('average.png', average_test.astype(np.uint8))
cv2.imwrite('mode.png', mode_result.astype(np.uint8))

cv2.waitKey(0)

#gentle quit
cap.release()
cv2.destroyAllWindows()