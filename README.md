Amanda Grace Wall & Eric Wan  
Georgia Tech Computational Photography (CS 4475)  
Spring 2016  

Facial Feature Swapping and Editing  

Written on Python 2.7.11

HOW TO USE:
 1) python main.py
 2) have two people in front of the camera
 3) enjoy the results!




HOW TO BUILD:
As far as we can tell, OSX seems to require the following commands:

brew install boost --with-python
brew install boost-python
<!--  potentially unnecessary -->
sudo chown -R $USER:admin /usr/local/include

brew link boost
brew install cmake
<!--  potentially unnecessary -->
sudo ln -s /opt/X11/include/X11 /usr/local/include/X11

sudo pip install dlib

Make sure to download and extract shape_predictor_68_face_landmarks.dat.zip into the project directory!
http://sourceforge.net/projects/dclib/files/dlib/v18.10/shape_predictor_68_face_landmarks.dat.bz2
