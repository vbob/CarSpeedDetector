import cv2
import sys
import time
import tensorflow as tf
import numpy as np

video = cv2.VideoCapture("v7.mp4")

if not video.isOpened():
    print("Could not open video")
    sys.exit()

totalFPS = 0
totalFrames = 0
timer = cv2.getTickCount()

btn_down = False

def get_points(im):
    # Set up data to send to mouse handler
    data = {}
    data['im'] = im.copy()
    data['lines'] = []

    # Set the callback function for any mouse event
    cv2.imshow("Image", im)
    cv2.setMouseCallback("Image", mouse_handler, data)
    cv2.waitKey(0)

    # Convert array to np.array in shape n,2,2
    points = np.uint16(data['lines'])
    print(points)

    return points, data['im']

def mouse_handler(event, x, y, flags, data):
    global btn_down

    if event == cv2.EVENT_LBUTTONUP and btn_down:
        #if you release the button, finish the line
        btn_down = False
        data['lines'][0].append((x, y)) #append the seconf point
        cv2.circle(data['im'], (x, y), 3, (0, 0, 255),5)
        cv2.line(data['im'], data['lines'][0][0], data['lines'][0][1], (0,0,255), 2)
        cv2.imshow("Image", data['im'])

    elif event == cv2.EVENT_MOUSEMOVE and btn_down:
        #thi is just for a ine visualization
        image = data['im'].copy()
        cv2.line(image, data['lines'][0][0], (x, y), (0,0,0), 1)
        cv2.imshow("Image", image)

    elif event == cv2.EVENT_LBUTTONDOWN and len(data['lines']) < 2:
        btn_down = True
        data['lines'].insert(0,[(x, y)]) #prepend the point
        cv2.circle(data['im'], (x, y), 3, (0, 0, 255), 5, 16)
        cv2.imshow("Image", data['im'])


# Read the graph.
with tf.gfile.FastGFile('./resnet_v2_283776.pb', 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())

with tf.Session() as sess:
    sess.graph.as_default()
    tf.import_graph_def(graph_def, name='')
    start_time = time.time()
    while (video.isOpened()):
        k, img = video.read()

        if not k:
            break
        img = cv2.resize(img, (1280, 720))
        totalFPS += cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        totalFrames += 1
        timer = cv2.getTickCount()

        rows = img.shape[0]
        cols = img.shape[1]
        inp = cv2.resize(img, (300, 300))
        inp = inp[:, :, [2, 1, 0]]  # BGR2RGB

        # Run the model
        with tf.device('/gpu:0'):
            out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                            sess.graph.get_tensor_by_name('detection_scores:0'),
                            sess.graph.get_tensor_by_name('detection_boxes:0'),
                            sess.graph.get_tensor_by_name('detection_classes:0')],
                        feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})

        num_detections = int(out[0][0])

        for i in range(num_detections):
            classId = int(out[3][0][i])
            score = float(out[1][0][i])
            bbox = [float(v) for v in out[2][0][i]]
            if score > 0.9:
                x = bbox[1] * cols
                y = bbox[0] * rows
                right = bbox[3] * cols
                bottom = bbox[2] * rows
                cv2.rectangle(img, (int(x), int(y)), (int(right),
                                                     int(bottom)), (125, 255, 51), thickness=2)
        pts, final_image = get_points(img)
        cv2.imshow('TensorFlow MobileNet-SSD', img)
        k = cv2.waitKey() & 0xff
        if k == 27: 
            break

print("Average FPS: " + str(int(totalFPS/totalFrames)) + " FPS")
print("Total Frames: " + str(totalFrames))
print("--- %s seconds ---" % (time.time() - start_time))
print("--- %.3f frametime ---" % ((time.time() - start_time)/totalFrames))