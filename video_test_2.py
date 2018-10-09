from __future__ import division
import dlib
import cv2
import numpy as np
import math
import csv


def resize(img, width=None, height=None, interpolation=cv2.INTER_AREA):
    global ratio
    w, h = img.shape

    if width is None and height is None:
        return img
    elif width is None:
        ratio = height / h
        width = int(w * ratio)
        resized = cv2.resize(img, (height, width), interpolation)
        return resized
    else:
        ratio = width / w
        height = int(h * ratio)
        resized = cv2.resize(img, (height, width), interpolation)
        return resized
def distance(x,y):
    return math.sqrt( (x[1] - y[1])**2 + (x[0] - y[0])**2 )

def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)

    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    # return the list of (x, y)-coordinates
    return coords

cap = cv2.VideoCapture(0)

predictor_path = 'shape_predictor_68_face_landmarks.dat'

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

with open('features.csv', 'a') as f:
    wr = csv.writer(f, dialect='excel')

    while True:

        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dets = detector(gray, 1)


        if len(dets) > 0:
            shape = predictor(gray, dets[0])
            shape = shape_to_np(shape)

            # for (x, y) in shape:
            #     cv2.circle(img, (x,y), 3, (255, 255, 255), -1)
            right_lip = tuple(shape[48])
            left_lip = tuple(shape[54])
            lip_len = distance(right_lip, left_lip)

            top_lip = tuple(shape[51])
            bottom_lip = tuple(shape[57])
            lip_width = distance(top_lip, bottom_lip)

            cv2.line(img, right_lip, left_lip, (255, 0, 0), 5)
            cv2.line(img, top_lip, bottom_lip, (255, 0, 0), 5)

            eye_border_len = distance(shape[36], shape[45])
            eye_inner_len = distance(shape[39], shape[42])
            cv2.line(img, tuple(shape[36]), tuple(shape[45]), (255, 255, 255), 2)
            cv2.line(img, tuple(shape[39]), tuple(shape[42]), (0, 0, 255), 2)

            nose_left = shape[35]
            nose_right = shape[31]

            eye_ratio = eye_border_len / eye_inner_len
            lip_ratio = lip_len / lip_width
            # print(lip_ratio, 'lip')
            # print(eye_ratio,'eye')

            right_angle = round(math.degrees(math.atan(abs(right_lip[1] - nose_left[1]) / abs(nose_left[0] - right_lip[0]))), 3)
            left_angle = round(math.degrees(math.atan(abs(left_lip[1] - nose_right[1]) / abs(nose_right[0] - left_lip[0]))), 3)
            right_right_angle = round(math.degrees(math.atan(abs(right_lip[1] - nose_right[1]) / abs(nose_right[0] - right_lip[0]))),3)
            left_left_angle = round(math.degrees(math.atan(abs(left_lip[1] - nose_left[1]) / abs(nose_left[0] - left_lip[0]))),3)

            write_list = [right_angle, right_right_angle, left_angle, left_left_angle, lip_ratio, eye_ratio]
            wr.writerow(write_list)
            print(right_angle, right_right_angle, left_angle, left_left_angle)

        cv2.imshow('image', img)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            cap.release()
            break