
import cv2
import numpy as np
import glob

import argparse
import pyautogui


max_value = 255
max_type = 4
max_binary_value = 255
trackbar_type = 'Type: \n 0: Binary \n 1: Binary Inverted \n 2: Truncate \n 3: To Zero \n 4: To Zero Inverted'
trackbar_value = 'Value'
trackbar_blur = 'Blur kernel size'
window_name = 'Gesture Tracking and Recognition'
isColor = False

def nothing(x):
    pass
    

cam = cv2.VideoCapture(0)
cv2.namedWindow(window_name)
cv2.createTrackbar(trackbar_type, window_name , 3, max_type, nothing)
# Create Trackbar to choose Threshold value
cv2.createTrackbar(trackbar_value, window_name , 0, max_value, nothing)
# Call the function to initialize
cv2.createTrackbar(trackbar_blur, window_name , 1, 20, nothing)
# create switch for ON/OFF functionality
color_switch = 'Color'
cv2.createTrackbar(color_switch, window_name,0,1,nothing)
cv2.createTrackbar('Contours', window_name,0,1,nothing)
lower_HSV = np.array([15, 70, 20], dtype = "uint8")  
upper_HSV = np.array([25, 255, 255], dtype = "uint8") 
lower_YCrCb = np.array((7, 140, 80), dtype = "uint8")  
upper_YCrCb = np.array((255, 173, 133), dtype = "uint8") 

def ZoomIn():
    pyautogui.hotkey('command', '+') 

def ZoomOut():
    pyautogui.hotkey('command', '-')

def Yeah():
    pyautogui.write('Hello world!') 

def Okay():
    pyautogui.write('Okay') 


while True:
    ret, frame = cam.read()
    if not ret:
        print('no cam')
        break
    
    #0: Binary
    #1: Binary Inverted
    #2: Threshold Truncated
    #3: Threshold to Zero
    #4: Threshold to Zero Inverted
    threshold_type = cv2.getTrackbarPos(trackbar_type, window_name)
    threshold_value = cv2.getTrackbarPos(trackbar_value, window_name)
    blur_value = cv2.getTrackbarPos(trackbar_blur, window_name)
    blur_value = blur_value+ (  blur_value%2==0)
    isColor = (cv2.getTrackbarPos(color_switch, window_name) == 1)
    findContours = (cv2.getTrackbarPos('Contours', window_name) == 1)
    
    #convert to grayscale
    if isColor == False:
    
        # HSV Method
        convertedHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  
        skinMaskHSV = cv2.inRange(convertedHSV, lower_HSV, upper_HSV)
    
        
        # YCrCb
        convertedYCrCb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)  
        skinMaskYCrCb = cv2.inRange(convertedYCrCb, lower_YCrCb, upper_YCrCb)
        
        skinMask = cv2.add(skinMaskHSV,skinMaskYCrCb) 
          # blur the mask to help remove noise, then apply the  
        # # mask to the frame  

        #threshold and binarize 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0) 
        # skin = cv2.bitwise_and(gray, gray, mask = skinMask) 

        # skin = gray

        ret, thresh = cv2.threshold(gray, 0, max_binary_value, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # skin[skin > 0.05] = 255
        # thresh = skin

        _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        contours=sorted(contours,key=cv2.contourArea,reverse=True) 
        fingerCount = 0
        fingerPts = []
        anglepts=[]
        if len(contours)>1:  
            largestContour = contours[0]  
            hull= cv2.convexHull(largestContour, returnPoints = False)    
            img = thresh
            offsetX=0
            offsetY=0
            scaleX=1920/img.shape[0]
            scaleY=1080/img.shape[1]
            for cnt in contours[:1]:  
                
                defects = cv2.convexityDefects(cnt,hull)  
                if(not isinstance(defects,type(None))):  
                    for i in range(defects.shape[0]):  
                        s,e,f,d = defects[i,0]    
                        start = tuple(cnt[s][0])  
                        end = tuple(cnt[e][0])  
                        far = tuple(cnt[f][0])  
                        c_squared = (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2  
                        a_squared = (far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2  
                        b_squared = (end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2  
                        angle = np.arccos((a_squared + b_squared  - c_squared ) / (2 * np.sqrt(a_squared * b_squared )))   
           
                        
                                            
                        if angle <= np.pi / 3:  
                            fingerCount += 1  
                            cv2.circle(thresh,far,5,[0,0,255],-1) 
                            
                            fingerPts.append(far)
                            anglepts.append(angle)
                            

                        cv2.line(thresh,start,end,[0,255,0],2) 
              
                        M = cv2.moments(largestContour)
                        cX = offsetX + scaleX *int(M["m10"] / M["m00"]) 
                        cY = offsetY + scaleY *int(M["m01"] / M["m00"]) 

                        # print(cX, cY)
      
                

                print(anglepts)
        
                skin = img
        fingerCount = fingerCount +1
        Anglethrehold = np.pi/6
        if fingerCount == 2 and anglepts[0] < Anglethrehold :
            ZoomOut()  #gesture 1 
        else:
            if fingerCount == 2 and anglepts[0] >= Anglethrehold:
                ZoomIn() #gesutre 2
        
        if fingerCount ==5:
            Yeah()
        if fingerCount ==3:
            Okay()
  
        print(fingerCount)
        print(fingerPts)
        print(len(anglepts))
        # print('Resolution: ' + str(img.shape[0]) + ' x ' + str(img.shape[1]))
        org = (50,50)
        font = cv2.FONT_HERSHEY_SIMPLEX 
        fontScale = 1
        thickness = 2
        color = (0, 0, 255)
        skin = cv2.putText(skin, str(fingerCount), org, font,  
                   fontScale, color, thickness, cv2.LINE_AA) 


    
    cv2.imshow(window_name, skin)

    k = cv2.waitKey(1) #k is the key pressed
    if k == 27 or k==113:  #27, 113 are ascii for escape and q respectively
        #exit
        cv2.destroyAllWindows()
        cam.release()
        print (k)
        break
