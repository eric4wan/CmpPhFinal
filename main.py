import sys
import os
import dlib
import cv2
import numpy

# https://github.com/burningion/faceswap/blob/master/swapfacesvideo.py
# http://www.kpkaiser.com/programming/the-mostly-newbies-guide-to-automatically-swapping-faces-in-video/

PREDICTOR_PATH = "/Users/ericwan/Downloads/shape_predictor_68_face_landmarks.dat"
SCALE_FACTOR = 1
FEATHER_AMOUNT = 11

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))

# Points used to line up the images.
ALIGN_POINTS = (LEFT_BROW_POINTS + RIGHT_EYE_POINTS + LEFT_EYE_POINTS +
                               RIGHT_BROW_POINTS + NOSE_POINTS + MOUTH_POINTS)

# Points from the second image to overlay on the first. The convex hull of each
# element will be overlaid.
OVERLAY_POINTS = [
    LEFT_EYE_POINTS + RIGHT_EYE_POINTS + LEFT_BROW_POINTS + RIGHT_BROW_POINTS,
    NOSE_POINTS + MOUTH_POINTS,
]

# Amount of blur to use during colour correction, as a fraction of the
# pupillary distance.
COLOUR_CORRECT_BLUR_FRAC = 0.6

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)
def draw_convex_hull(im, points, color):
    points = cv2.convexHull(points)
    cv2.fillConvexPoly(im, points, color=color)


def warp_im(im, M, dshape):
    output_im = numpy.zeros(dshape, dtype=im.dtype)
    cv2.warpAffine(im,
                   M[:2],
                   (dshape[1], dshape[0]),
                   dst=output_im,
                   borderMode=cv2.BORDER_TRANSPARENT,
                   flags=cv2.WARP_INVERSE_MAP)
    return output_im

def get_face_mask(im, landmarks):
    im = numpy.zeros(im.shape[:2], dtype=numpy.float64)

    for group in OVERLAY_POINTS:
        draw_convex_hull(im,
                         landmarks[group],
                         color=1)

    im = numpy.array([im, im, im]).transpose((1, 2, 0))

    im = (cv2.GaussianBlur(im, (FEATHER_AMOUNT, FEATHER_AMOUNT), 0) > 0) * 1.0
    im = cv2.GaussianBlur(im, (FEATHER_AMOUNT, FEATHER_AMOUNT), 0)

    return im

def faceSwap():
    print("Analyzing your photos...")
    if (findNumFaces() < 2):
        print("Whoops! Looks like we couldn't find more than one face to swap. Please try again!")
        sys.exit(0)
    print("Starting faceswap...")
    out_list = []
    # add result to out_list



    writeOutput(out_list)
    return True

def transformation_from_points(points1, points2):
    """
    Return an affine transformation [s * R | T] such that:
        sum ||s*R*p1,i + T - p2,i||^2
    is minimized.
    """
    # Solve the procrustes problem by subtracting centroids, scaling by the
    # standard deviation, and then using the SVD to calculate the rotation. See
    # the following for more details:
    #   https://en.wikipedia.org/wiki/Orthogonal_Procrustes_problem

    points1 = points1.astype(numpy.float64)
    points2 = points2.astype(numpy.float64)

    c1 = numpy.mean(points1, axis=0)
    c2 = numpy.mean(points2, axis=0)
    points1 -= c1
    points2 -= c2

    s1 = numpy.std(points1)
    s2 = numpy.std(points2)
    points1 /= s1
    points2 /= s2

    U, S, Vt = numpy.linalg.svd(points1.T * points2)

    # The R we seek is in fact the transpose of the one given by U * Vt. This
    # is because the above formulation assumes the matrix goes on the right
    # (with row vectors) where as our solution requires the matrix to be on the
    # left (with column vectors).
    R = (U * Vt).T

    return numpy.vstack([numpy.hstack(((s2 / s1) * R,
                                       c2.T - (s2 / s1) * R * c1.T)),
                         numpy.matrix([0., 0., 1.])])

def test(im):
    rects = detector(im, 1)
    print("@@@@@@")
    print(len(rects))
    im1, landmarks1 = (im, numpy.matrix([[p.x, p.y] for p in predictor(im, rects[0]).parts()])) # first detected face
    im2, landmarks2 = (im, numpy.matrix([[p.x, p.y] for p in predictor(im, rects[1]).parts()])) # second detected face

    M = transformation_from_points(landmarks1[ALIGN_POINTS], # First transformation
                                   landmarks2[ALIGN_POINTS])

    M1 = transformation_from_points(landmarks2[ALIGN_POINTS], # Second transformation
                                   landmarks1[ALIGN_POINTS])

    mask = get_face_mask(im2, landmarks2) # First mask
    mask1 = get_face_mask(im1, landmarks1) # Second mask

    warped_mask = warp_im(mask, M, im1.shape) # First warp
    warped_mask1 = warp_im(mask1, M1, im2.shape) # Second warp

    combined_mask = numpy.max([get_face_mask(im1, landmarks1), warped_mask],
                              axis=0)
    combined_mask1 = numpy.max([get_face_mask(im2, landmarks2), warped_mask1],
                              axis=0)

    warped_corrected_im2 = correct_colours(im1, warped_im2, landmarks1)
    warped_corrected_im3 = correct_colours(im2, warped_im3, landmarks2)

    output_im = im1 * (1.0 - combined_mask) + warped_corrected_im2 * combined_mask # apply first mask
    output_im = output_im * (1.0 - combined_mask1) + warped_corrected_im3 * combined_mask1 # apply second face mask

    cv2.imwrite('output.jpg', output_im)

def filters():
    print("Analyzing your photos...")


def findNumFaces():
    # sourcefolder = os.path.abspath(os.path.join(os.curdir, 'source'))
    # outfolder = os.path.abspath(os.path.join(os.curdir, 'out'))
    # if not os.path.exists(outfolder):
    #     os.mkdir(outfolder)
    #
    # exts = ['.bmp', '.pbm', '.pgm', '.ppm', '.sr', '.ras', '.jpeg', '.jpg',
    #         '.jpe', '.jp2', '.tiff', '.tif', '.png']
    # numFaces = 0
    # img_list = []
    # for dirA in os.listdir(sourcefolder):
    #     img_list = []
    #     filenames = sorted(os.listdir(os.path.join(sourcefolder, dirA)))
    #
    #     for filename in filenames:
    #         name, ext = os.path.splitext(filename)
    #         if ext in exts:
    #             img_list.append(cv2.imread(os.path.join(sourcefolder, video_dir,
    #                                                     filename)))
    # # for img in img_list:
    #     # set numFaces

    return 2


def writeOutput(out_list):
    print "writing output to {}".format(os.path.join(outfolder, video_dir))
    if not os.path.exists(os.path.join(outfolder, video_dir)):
        os.mkdir(os.path.join(outfolder, video_dir))

    for idx, image in enumerate(out_list):
        cv2.imwrite(os.path.join(outfolder,video_dir,'frame{0:04d}.png'.format(idx)), image)

if __name__ == "__main__":
    # faceOrFilter = input("Hello! Would you like to try faceSwap or filter? ")
    image = cv2.imread("source/fs.jpeg", cv2.IMREAD_GRAYSCALE)
    test(image)
    feature = -1
    # -1 = not valid
    # 0 = FaceSwap
    # 1 = filter
    if (faceOrFilter == "FaceSwap"):
        faceSwap()
    elif (faceOrFilter == "Filter"):
        filters()
    else:
        print("That was not valid input!")
        sys.exit(0)
