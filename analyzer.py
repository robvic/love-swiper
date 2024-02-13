import glob
import statistics as st
import cv2
import numpy as np

counter = 0
files = glob.glob('./pics/*.jpg')
gender_model = cv2.dnn.readNetFromCaffe('./models/gender_deploy.prototxt.txt', './models/gender_net.caffemodel')
for file in files:
    print(file)

    img = cv2.imread(file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier('./models/haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    for (x, y, w, h) in faces:
        face_roi = img[y:y+h, x:x+w]
        face_color = np.average(img, axis=(0,1))
        face_proportion = ((h*w)/(img.shape[0]*img.shape[1]))
        face_blob = cv2.dnn.blobFromImage(face_roi, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
        gender_model.setInput(face_blob)
        gender_preds = gender_model.forward()
        gender = 'Male' if gender_preds[0][0] > gender_preds[0][1] else 'Female'
        color = (0, 0, 255) if gender=='Male' else (0, 255, 0)
        cv2.putText(img, gender, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
    perc_threshold = 0.3
    b_min = face_color[0]*(1-perc_threshold)
    r_min = face_color[1]*(1-perc_threshold)
    g_min = face_color[2]*(1-perc_threshold)
    b_max = face_color[0]*(1+perc_threshold)
    r_max = face_color[1]*(1+perc_threshold)
    g_max = face_color[2]*(1+perc_threshold)
    pixel_count = 0
    h, w = img.shape[:2]
    for i in range(h):
        for j in range(w):
            pixel_color = img[i,j]
            if b_min<pixel_color[0]<b_max and r_min<pixel_color[1]<r_max and g_min<pixel_color[2]<g_max: pixel_count+=1
    print(pixel_count)
    cv2.putText(img, ("Skin ratio: "+str(pixel_count/(h*w))), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(img, ("Face sample: "+str(pixel_color)), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(img, ("Face area: "+str(x*y)), (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imshow('Pic', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    counter =+ 1
    if counter >10:
        break
    
# TODO: - Identify fullbody
#       - Evaluate naked body proportion

# Get mean pixel color value inside face_roi
## face_color = np.average(img, axis=(0,1))
# Calculate proportion of face_roi and img resolution
## face_proportion = (img.size[0]*img.size[1])/h*w
# Calculate proportion of color range inside full img
## perc_threshold = 0.1
## pixel_count = 0
## for (x, y) in enumerate(img):
##  pixel_color = img[x,y]
##  if face_color*(1+perc_threshold)>pixel_color>face_color*(1-perc_threshold):pixel_count=+1
## print(pixel_count)
# If color range is above threshold, render label