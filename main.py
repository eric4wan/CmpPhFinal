#!/usr/bin/python

# Copyright (c) 2015 Matthew Earl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
#     NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#     DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#     OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#     USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

Please consult the README on build instructions! There are a lot of things to do.

Small sections of this code were borrowed (legally/ethically/rightfully) from
online resources. A Copyright statement from one author has been included above,
as per their request.

The pipeline was completely written from scratch, including the webcam frame/output
manipulation. The transformation matrix was painstakingly derived from wiki but then
StackOverflow provided a *cough* somewhat insignificant* inspirational resource.

Other sources were used as slight references, but this code is ultimately *ours* -
we wrote it and it's ours and we wrote it. Enjoy!

Eric Wan
Amanda Grace Wall
"""

import cv2
import dlib
import numpy as np
import sys
import glob
import shutil

# dlib has a 62 'hardcoded' facial landmarks to look for
# the necessary ones are enumerated here
MOUTH = list(range(48, 61))
RIGHT_BROW = list(range(17, 22))
LEFT_BROW = list(range(22, 27))
RIGHT_EYE = list(range(36, 42))
LEFT_EYE = list(range(42, 48))
NOSE = list(range(27, 35))

# points used to line up the images.
ALIGN_POINTS = (LEFT_BROW + RIGHT_EYE + LEFT_EYE +
                               RIGHT_BROW + NOSE + MOUTH)

# will need the convex hull of each of these elemnts to overlay on face 1 from face 2
OVERLAY_POINTS = []

# basically a switch function
def excl(arg):
    switch = {
        'A': [LEFT_EYE + RIGHT_EYE + LEFT_BROW + RIGHT_BROW,
        NOSE + MOUTH,],
        'E': [LEFT_EYE + RIGHT_EYE,],
        'N': [NOSE,],
        'M': [MOUTH,]
    }
    return switch.get(arg, "INVALID INPUT")

# start of keyboard input to control the faceswap parameters
bo = raw_input("\nHello! Welcome to live FaceSwap. \nWould you like to begin or review the options? ('B' or 'O')\n")
if (bo == "O"):
    ex = raw_input("\nWhich features would you like to swap? Please type only one letter and hit enter to add it to the list.\n\
        All features = 'A'\n Eyes = 'E'\n Nose = 'N'\n Mouth = 'M'\n")
    OVERLAY_POINTS = excl(ex)

if (bo == "B"):
    OVERLAY_POINTS = [LEFT_EYE + RIGHT_EYE + LEFT_BROW + RIGHT_BROW, NOSE + MOUTH,]

if (((bo != "B") and (bo != "O")) or len(OVERLAY_POINTS) == 0):
    print "QUITTING"
    sys.exit(0)

detector = dlib.get_frontal_face_detector()
# make sure it's here!!!
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def face_outline(im, landmarks, rain):
    im = np.zeros(im.shape[:2], dtype = np.float64)
    points = None
    if rain:
        points = [MOUTH,]
    else:
        points = OVERLAY_POINTS

    for group in points:
        points = cv2.convexHull(landmarks[group])
        cv2.fillConvexPoly(im, landmarks[group], color = 1)

    im = np.array([im, im, im]).transpose((1, 2, 0))

    im = (cv2.GaussianBlur(im, (11, 11), 0) > 0) * 1.0
    im = cv2.GaussianBlur(im, (11, 11), 0)

    return im

def transformation_matrix(points1, points2):
    # computing the affine transofmration [s * R | T] to minimize
    #   67
    #  SIGMA || s * R * points1 + T - points2 ||^2
    #   0
    # reference: https://en.wikipedia.org/wiki/Orthogonal_Procrustes_problem
    points1 = points1.astype(np.float64)
    points2 = points2.astype(np.float64)
    # subtract centroids
    c1 = np.mean(points1, axis=0)
    c2 = np.mean(points2, axis=0)
    points1 -= c1
    points2 -= c2
    # scale by standard deviation
    s1 = np.std(points1)
    s2 = np.std(points2)
    points1 /= s1
    points2 /= s2
    # use SVD to get rotation
    U, S, Vt = np.linalg.svd(points1.T * points2)
    # actually need the matrix on the left
    R = (U * Vt).T
    outVal = np.vstack([np.hstack(((s2 / s1) * R, c2.T - (s2 / s1) * R * c1.T)), np.matrix([0., 0., 1.])])
    return outVal

def warp_im(im, M, dshape):
    # applies the affine transformation
    output_im = np.zeros(dshape, dtype = im.dtype)
    cv2.warpAffine(im, M[:2], (dshape[1], dshape[0]), dst = output_im, borderMode = cv2.BORDER_TRANSPARENT, flags = cv2.WARP_INVERSE_MAP)
    return output_im

def color_correction(im1, im2, landmarks1):
    blur_amount = 0.6 * np.linalg.norm(np.mean(landmarks1[LEFT_EYE], axis = 0) - np.mean(landmarks1[RIGHT_EYE], axis = 0))
    blur_amount = int(blur_amount)
    if blur_amount % 2 == 0:
        blur_amount += 1
    im1_blur = cv2.GaussianBlur(im1, (blur_amount, blur_amount), 0)
    im2_blur = cv2.GaussianBlur(im2, (blur_amount, blur_amount), 0)
    # avoid type conversion and div by zero errors
    im2_blur += (128 * (im2_blur <= 1)).astype(np.uint8)
    out_val = (im2.astype(np.float64) * im1_blur.astype(np.float64) / im2_blur.astype(np.float64))
    return out_val

def tintMouthRed(im, landmarks1):
    blur_amount = 0.6 * np.linalg.norm(np.mean(landmarks1[LEFT_EYE], axis = 0) - np.mean(landmarks1[RIGHT_EYE], axis = 0))
    blur_amount = int(blur_amount)
    if blur_amount % 2 == 0:
        blur_amount += 1
    imblur = cv2.GaussianBlur(im, (blur_amount, blur_amount), 0)

    red = np.ones(im.shape, dtype = np.float64)
    red[red[:,:,0] > 0] = [10, 10, 100]
    redblur = cv2.GaussianBlur(red, (blur_amount, blur_amount), 0)
    imblur += (128 * (imblur <= 1)).astype(np.uint8)
    return (im.astype(np.float64) * red / imblur.astype(np.float64))

webcam = cv2.VideoCapture(0)
counter = 0
fsaved = False

while True:
    # avoid lag by waiting
    counter += 1
    if (counter % 3 == 0):
        ret, frame = webcam.read()
        saved = frame
        # detect faces from current webcam frame
        faces = detector(frame, 1)
        if len(faces) < 2:
            # print "need more faces!!!"
            if (len(faces) == 1):
                imRain, landmRain = (saved, np.matrix([[p.x, p.y] for p in predictor(frame, faces[0]).parts()]))
                mouth = face_outline(imRain, landmRain, True)
                colored = tintMouthRed(imRain, landmRain)
                saved = saved * (1.0 - mouth) + colored * mouth
                saved =  np.array(saved, dtype = float) / float(255)
                cv2.imshow('2', saved)
            continue
        else:
            # because both faces show up in same frame, ordering is important for xy math
            if faces[0].left() < faces[1].left():
                im1, landmarks1 = (frame, np.matrix([[p.x, p.y] for p in predictor(frame, faces[0]).parts()]))
                im2, landmarks2 = (frame, np.matrix([[p.x, p.y] for p in predictor(frame, faces[1]).parts()]))
            else:
                im1, landmarks1 = (frame, np.matrix([[p.x, p.y] for p in predictor(frame, faces[1]).parts()]))
                im2, landmarks2 = (frame, np.matrix([[p.x, p.y] for p in predictor(frame, faces[0]).parts()]))

            # get transformation matrices
            M = transformation_matrix(landmarks1[ALIGN_POINTS], landmarks2[ALIGN_POINTS])
            M1 = transformation_matrix(landmarks2[ALIGN_POINTS], landmarks1[ALIGN_POINTS])
            # get actual chunk of face (if swapping all features, should look like a 'T')
            mask = face_outline(im2, landmarks2, False)
            mask1 = face_outline(im1, landmarks1, False)
            # applying the transformation to the masks
            warped_mask = warp_im(mask, M, im1.shape)
            warped_mask1 = warp_im(mask1, M1, im2.shape)
            # combining
            combined_mask = np.max([face_outline(im1, landmarks1, False), warped_mask], axis = 0)
            combined_mask1 = np.max([face_outline(im2, landmarks2, False), warped_mask1], axis = 0)
            warped_im2 = warp_im(im2, M, im1.shape)
            warped_im3 = warp_im(im1, M1, im2.shape)
            # blending skin colors
            warped_corrected_im2 = color_correction(im1, warped_im2, landmarks1)
            warped_corrected_im3 = color_correction(im2, warped_im3, landmarks2)
            # finishing off transformation math
            output_im = im1 * (1.0 - combined_mask) + warped_corrected_im2 * combined_mask
            output_im = output_im * (1.0 - combined_mask1) + warped_corrected_im3 * combined_mask1
            # format for cv2.imshow() - if you want to use cv2.imwrite(), skip this line
            output_im =  np.array(output_im, dtype = float) / float(255)
            cv2.imshow('frame', output_im)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


webcam.release()
cv2.destroyAllWindows()
print "\nBye - thanks for trying out FaceSwap!"
