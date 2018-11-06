import cv2
import sys
import os
os.environ["PYSDL2_DLL_PATH"] = "C:\\Users\\vbob\\Downloads\\PySDL2-0.9.5\\sdl2"

import sdl2.ext 
 
# Open the video
#video = cv2.VideoCapture("videos/CARSPEED2-FF-SHDW.mp4")
#video = cv2.VideoCapture("videos/CARSPEED3-FF-MC.mp4")
#video = cv2.VideoCapture("videos/CARSPEED6-FF-MC_OC.mp4")
video = cv2.VideoCapture("videos/40KMH_2.mp4")

# Exit if video not opened.
if not video.isOpened():
    print("Could not open video")
    sys.exit()

# Read first frame.
ok, frame = video.read()
frame = cv2.resize(frame, (1280, 720))
if not ok:
    print('Cannot read video file')
    sys.exit()

# Average FPS
totalFPS = 0
totalFrames = 0
timer = cv2.getTickCount()

# Tracker
tracker = cv2.TrackerMedianFlow_create()
#tracker = cv2.TrackerTLD_create()
bbox = cv2.selectROI(frame, False)
ok = tracker.init(frame, bbox)

# Line Configurations
# CARSPEED2-FF-SHDW.mp4
#l1Start = (250,200)
#l1End = (440,260)
#l2Start = (316,125)
#l2End = (500,185)

# CARSPEED3-FF-MC.mp4
#l1Start = (380,276)
#l1End = (516,374)
#l2Start = (455,226)
#l2End = (590,320)

# CARSPEED6-FF-MC_OC.mp4
#l1Start = (276,254)
#l1End = (414,346)
#l2Start = (362,189)
#l2End = (500,285)

# # 40KMH_2.mp4
l1Start = (691,391)
l1End = (795, 266)
l2Start = (474,308)
l2End = (572,178)

# 10.mp4
# l2Start = (81,31)
# l2End = (1240,31)
# l1Start = (81,131)
# l1End = (1240,131)



# Frame Count
numberFrames = 0;
touchedGreen = 0;
touchedRed = 0;
frameArray = []

while (video.isOpened()):
    # Read Current Frame
    ok, frame = video.read()
    frame = cv2.resize(frame, (1280, 720))
    if (not ok):
        break

    # Add lines
    cv2.line(frame,l1Start,l1End,(0,255,0),2)
    cv2.line(frame,l2Start,l2End,(0,0,255),2)

    # Update Tracker
    ok, bbox = tracker.update(frame)

    # If Tracker Succeeded
    if ok:
        # Tracking success
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        frameArray.append((int((p1[0]+p2[0])/2),int((p1[1]+p2[1])/2)))
        if not sdl2.ext.liangbarsky(p1[0],p1[1],p2[0],p2[1],l1Start[0],l1Start[1],l1End[0],l1End[1])[0] == None:
            #print(sdl2.ext.liangbarsky(p1[0],p1[1],p2[0],p2[1],l1Start[0],l1Start[1],l1End[0],l1End[1]))
            cv2.rectangle(frame, p1, p2, (0,255,0), 2, -1)
            for row in frameArray:
                cv2.circle(frame, row, 1, (0,255,0), 2, -1)
            touchedGreen = 1;
        elif not sdl2.ext.liangbarsky(p1[0],p1[1],p2[0],p2[1],l2Start[0],l2Start[1],l2End[0],l2End[1])[0] == None:
            cv2.rectangle(frame, p1, p2, (0,0,255), 2, -1)
            for row in frameArray:
                cv2.circle(frame, row, 1, (0,0,255), 2, -1)
            touchedRed = 1;
        else: 
            for row in frameArray:
                cv2.circle(frame, row, 1, (255,0,0), 2, -1)
            cv2.rectangle(frame, p1, p2, (255,0,0), 2, -1)
    else :
        # Tracking failure
        cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    # If touched green, count frames
    if (touchedGreen == 1 and touchedRed == 0):
        numberFrames += 1
    elif (touchedRed == 1 and touchedGreen == 0):
        numberFrames += 1
    elif (touchedRed == 1 and touchedGreen == 1):
        cv2.putText(frame, "Estimated Speed: " + str(int((4/(numberFrames/30))*3.6)) + " Kph", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    # Display result
    cv2.imshow("DrawLine", frame)

    # Get FPS
    totalFPS += cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    totalFrames += 1
    timer = cv2.getTickCount()
    
    # Close if ESC    
    k = cv2.waitKey(1) & 0xff
    if k == 27: 
        break

# Show FPS
print("Average FPS: " + str(int(totalFPS/totalFrames)) + " FPS")
sys.exit()




def rectangleIntersectedByLine(rectTopLeft, rectBotRight, lineStart, lineEnd):
    minX = lineStart[0]
    maxX = lineEnd[0]

    if (lineStart[0] > lineEnd[0]):
        minX = lineEnd[0]
        maxX = lineStart[0]
    
    if (maxX > rectBotRight[0]):
        maxX = rectBotRight[0]

    if (minX < rectTopLeft[0]):
        minX = rectTopLeft[0]

    if (minX > maxX):
        return False

    minY = lineStart[1]
    maxY = lineEnd[1]

    dx = lineEnd[0] - lineStart[0]

    if (abs(dx) > 0.000001):
        a = (lineEnd[1] - lineStart[1])/dx
        b = lineStart[1] - a * lineStart[0]
        minY = a * minX + b
        maxY = a * maxX + b

    if (minY > maxY):
        tmp = maxY
        maxY = minY
        minY = tmp

    if (maxY > rectBotRight[1]):
        maxY = rectBotRight[1]

    if (minY < rectTopLeft[0]):
        maxY = rectTopLeft[0]

    if (minY > maxY):
        return False 

    return True

def intersection(a,b):
  x = max(a[0], b[0])
  y = max(a[1], b[1])
  w = min(a[0]+a[2], b[0]+b[2]) - x
  h = min(a[1]+a[3], b[1]+b[3]) - y
  if w<0 or h<0: return () # or (0,0,0,0) ?
  return (x, y, w, h)

