import cv2
import sys
 
# Open the video
#video = cv2.VideoCapture("videos/CARSPEED6-FF-MC_OC.mp4")
video = cv2.VideoCapture("videos/40KMH_2.mp4")
# Exit if video not opened.
if not video.isOpened():
    print("Could not open video")
    sys.exit()

# Read first frame.
ok, frame = video.read()
if not ok:
    print('Cannot read video file')
    sys.exit()

# Average FPS
totalFPS = 0
totalFrames = 0
timer = cv2.getTickCount()

while (video.isOpened()):
    # Read Current Frame
    ok, frame = video.read()
    if (not ok):
        break

        # Display result
    cv2.imshow("DrawLine", cv2.resize(frame, (1280, 720)))

    # Get FPS
    totalFPS += cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    totalFrames += 1
    timer = cv2.getTickCount()
    
    # Close if ESC    
    k = cv2.waitKey() & 0xff
    if k == 27: 
        break

# Show FPS
print("Average FPS: " + str(int(totalFPS/totalFrames)) + " FPS")
sys.exit()

