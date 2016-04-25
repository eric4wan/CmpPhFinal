if __name__ == "__main__":
    faceOrFilter = input("Hello! Would you like to try 'FaceSwap' or 'Filter'?")

    feature = -1
    # -1 = not valid
    # 0 = FaceSwap
    # 1 = filter
    if (faceOrFilter == 'FaceSwap'):
        faceSwap()
    else if (faceOrFilter == 'Filter'):
        filters()


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


def filters():
    print("Analyzing your photos...")


def findNumFaces():
    sourcefolder = os.path.abspath(os.path.join(os.curdir, 'videos', 'source'))
    outfolder = os.path.abspath(os.path.join(os.curdir, 'videos', 'out'))
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)

    exts = ['.bmp', '.pbm', '.pgm', '.ppm', '.sr', '.ras', '.jpeg', '.jpg',
            '.jpe', '.jp2', '.tiff', '.tif', '.png']
    numFaces = 0
    img_list = []
    for dirA in os.listdir(sourcefolder):
        img_list = []
        filenames = sorted(os.listdir(os.path.join(sourcefolder, dirA)))

        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext in exts:
                img_list.append(cv2.imread(os.path.join(sourcefolder, video_dir,
                                                        filename)))
    for img in img_list:
        # set numFaces

    return numFaces

def writeOutput(out_list):
    print "writing output to {}".format(os.path.join(outfolder, video_dir))
    if not os.path.exists(os.path.join(outfolder, video_dir)):
        os.mkdir(os.path.join(outfolder, video_dir))

    for idx, image in enumerate(out_list):
        cv2.imwrite(os.path.join(outfolder,video_dir,'frame{0:04d}.png'.format(idx)), image)
