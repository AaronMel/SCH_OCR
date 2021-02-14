import cv2
import numpy as np
import pytesseract
import os
import datetime


per = 25
pixelThreshold=500

"""
TDL
- replace set x,y,w,h coordinates with those from ocr for implementention (NOTE: coordinates are not real refer to the vid for more info )
    - create sorting filter for valuavble coordinate finding [DIČ etc.]
- import into source code 
"""
roi = [[(98, 984), (680, 1074), 'text', 'Name'],
       [(740, 980), (1320, 1078), 'text', 'Phone'],
       [(98, 1154), (150, 1200), 'box', 'Sign'],
       [(738, 1152), (790, 1200), 'box', 'Allergic'],
       [(100, 1418), (686, 1518), 'text', 'Email'],
       [(740, 1416), (1318, 1512), 'text', 'ID'],
       [(110, 1598), (676, 1680), 'text', 'City'],
       [(748, 1592), (1328, 1686), 'text', 'Country']]


################################## Image processing ##################################
"needs to be edited to be used as it relies on 'default' image to calculate the missing parts"
"thus it may be completely worthless as we do not use this format"
tc1 = datetime.datetime.now()

imgQueryPath = "input/Query.png"
imgFolder = "input/test/"

imgQ = cv2.imread(imgQueryPath)
h,w,c = imgQ.shape
orb = cv2.ORB_create(1000)
kp1, des1 = orb.detectAndCompute(imgQ,None)


myPicList = os.listdir(imgFolder)
print(myPicList)
for j,y in enumerate(myPicList):
    tp1 = datetime.datetime.now()
    img = cv2.imread(imgFolder + y)
    kp2, des2 = orb.detectAndCompute(img,None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.match(des2,des1)
    matches.sort(key= lambda x: x.distance)
    good = matches[:int(len(matches)*(per/100))]
    imgMatch = cv2.drawMatches(img,kp2,imgQ,kp1,good[:100],None,flags=2)

    srcPoints = np.float32([kp2[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dstPoints = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M, _ = cv2.findHomography(srcPoints,dstPoints,cv2.RANSAC,5.0)
    imgScan = cv2.warpPerspective(img,M,(w,h))

    imgShow = imgScan.copy()
    imgMask = np.zeros_like(imgShow)

    myData = []

    tp2 = datetime.datetime.now() - tp1
    print(tp2, " Image processing finish")

    ################################## ROI extraction ##################################
    "main body and the extraction point"

    print(f'################## Extracting Data from Form {j}  ##################')
    tr1 = datetime.datetime.now()
    
    for x,r in enumerate(roi):
        cv2.rectangle(imgMask, (r[0][0],r[0][1]),(r[1][0],r[1][1]),(0,255,0),cv2.FILLED)
        imgShow = cv2.addWeighted(imgShow,0.99,imgMask,0.1,0)

        imgCrop = imgScan[r[0][1]:r[1][1], r[0][0]:r[1][0]]

        if r[2] == 'text':
            print('{} :{}'.format(r[3],pytesseract.image_to_string(imgCrop)))
            myData.append(pytesseract.image_to_string(imgCrop))
            for item in myData:
                index = myData.index(item)

                if type(item) == int:
                    continue
                else:
                    item = item.replace("\n\x0c", "")
                    myData[index] = item

        if r[2] =='box':
            imgGray = cv2.cvtColor(imgCrop,cv2.COLOR_BGR2GRAY)
            imgThresh = cv2.threshold(imgGray,170,255, cv2.THRESH_BINARY_INV)[1]
            totalPixels = cv2.countNonZero(imgThresh)
            if totalPixels>pixelThreshold: totalPixels =1;
            else: totalPixels=0
            print(f'{r[3]} :{totalPixels}')
            myData.append(totalPixels)
        cv2.putText(imgShow,str(myData[x]),(r[0][0],r[0][1]),
                    cv2.FONT_HERSHEY_PLAIN,2.5,(0,0,255),4)
    print(myData)

    tr2 = datetime.datetime.now() - tr1
    print(tr2, " Roi extraction finish")
    cv2.imwrite(y,imgShow)

tc2 = datetime.datetime.now() - tc1
print(tc2, "Processes finished")

#cv2.imshow("KeyPointsQuery",impKp1)
#cv2.imshow("Output",imgQ)
#cv2.waitKey(0)



################################## Region Selector ##################################
"should be obsolete in final version and thus deleted before release"

"""
This script allows to collect raw points from an image.
The inputs are two mouse clicks one in the x,y position and
the second in w,h of a rectangle.
Once a rectangle is selected the user is asked to enter the type
and the Name:
Type can be 'Text' or 'CheckBox'
Name can be anything
"""

import random

path = 'Query.png'
scale = 0.5
circles = []
counter = 0
counter2 = 0
point1=[]
point2=[]
myPoints = []
myColor=[]
def mousePoints(event,x,y,flags,params):
    global counter,point1,point2,counter2,circles,myColor
    if event == cv2.EVENT_LBUTTONDOWN:
        if counter==0:
            point1=int(x//scale),int(y//scale);
            counter +=1
            myColor = (random.randint(0,2)*200,random.randint(0,2)*200,random.randint(0,2)*200 )
        elif counter ==1:
            point2=int(x//scale),int(y//scale)
            type = input('Enter Type')
            name = input ('Enter Name ')
            myPoints.append([point1,point2,type,name])
            counter=0
        circles.append([x,y,myColor])
        counter2 += 1
"""
img = cv2.imread(path)
img = cv2.resize(img, (0, 0), None, scale, scale)
while True:
    # To Display points
    for x,y,color in circles:
        cv2.circle(img,(x,y),3,color,cv2.FILLED)
    cv2.imshow("Original Image ", img)
    cv2.setMouseCallback("Original Image ", mousePoints)
    if cv2.waitKey(1) & 0xFF == ord('s'):
        print(myPoints)
        break
"""

def roi_finder(logFile, valuableList):
    
    base = {
        "roi": []
    }
    object = {
        "x": 0,
        "y": 0,
        "w": 0,
        "h": 0,
        "name": ""
    }
    base["roi"].append(object)
    return base