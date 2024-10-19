import cv2
import numpy as np
import os
import HandTrackingModule as htm

# Path for header images
folderPath = r"C:\Users\jayan\PycharmProjects\pythonProject\header2"
myList = os.listdir(folderPath)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    image = cv2.resize(image, (1280, 125))  # Resize the image to fit the header space
    overlayList.append(image)

# Initialize header and colors
header = overlayList[0]
drawColor = (255, 0, 255)
brushThickness = 15
eraserThickness = 100
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

# Shape selection variables
currentShape = None
shapeStart = (0, 0)
shapeEnd = (0, 0)
shapeDrawing = False

def virtual_Painter():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = htm.handDetector(detectionCon=0.85, maxHands=1)
    global xp, yp, imgCanvas, header, drawColor, brushThickness, currentShape, shapeStart, shapeEnd, shapeDrawing

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            # Tip positions
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            x0, y0 = lmList[4][1:]

            fingers = detector.fingersUp()

            # Selection mode - Two fingers up
            if fingers[1] and fingers[2]:
                xp, yp = 0, 0
                shapeDrawing = False

                # Checking for the click on header
                if y1 < 125:
                    if 250 < x1 < 450:
                        header = overlayList[0]
                        drawColor = (255, 0, 255)
                    elif 550 < x1 < 750:
                        header = overlayList[1]
                        drawColor = (255, 0, 0)
                    elif 800 < x1 < 950:
                        header = overlayList[2]
                        drawColor = (0, 255, 0)
                    elif 1050 < x1 < 1200:
                        header = overlayList[3]
                        drawColor = (0, 0, 0)

                # Checking for shape selection
                elif 125 < y1 < 210:
                    if 50 < x1 < 200:
                        currentShape = "rectangle"
                    elif 250 < x1 < 400:
                        currentShape = "circle"

                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

            # Drawing mode - Index finger up
            elif fingers[1] and not fingers[2]:
                if currentShape:
                    if not shapeDrawing:
                        shapeStart = (x1, y1)
                        shapeDrawing = True
                    shapeEnd = (x1, y1)

                else:
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1

                    if drawColor == (0, 0, 0):
                        cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
                    else:
                        cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

                    xp, yp = x1, y1

            # Shape drawing logic
            if shapeDrawing:
                if currentShape == "rectangle":
                    cv2.rectangle(img, shapeStart, shapeEnd, drawColor, brushThickness)
                    cv2.rectangle(imgCanvas, shapeStart, shapeEnd, drawColor, brushThickness)
                elif currentShape == "circle":
                    radius = int(((shapeEnd[0] - shapeStart[0]) ** 2 + (shapeEnd[1] - shapeStart[1]) ** 2) ** 0.5 / 2)
                    center = ((shapeStart[0] + shapeEnd[0]) // 2, (shapeStart[1] + shapeEnd[1]) // 2)
                    cv2.circle(img, center, radius, drawColor, brushThickness)
                    cv2.circle(imgCanvas, center, radius, drawColor, brushThickness)

        # Merge the canvas and video feed
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

        # Setting the header image
        img[0:125, 0:1280] = header

        cv2.imshow("Image", img)
        cv2.imshow("Canvas", imgCanvas)
        cv2.waitKey(1)


if _name_ == "_main_":
    print("Starting Virtual Painter")
    virtual_Painter()