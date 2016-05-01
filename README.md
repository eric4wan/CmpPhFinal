Amanda Grace Wall & Eric Wan  
Georgia Tech Computational Photography (CS 4475)  
Spring 2016  

Facial Feature Swapping and Editing  

Written on Python 2.7.11


As far as we can tell, OSX seems to require the following commands to acquire all dependencies.
However, I may have missed a few or gotten some out of order - I was consulting google for a
non-insignificant amount of time to get it working in the first place.

brew install boost --with-python
brew install boost-python
sudo chown -R $USER:admin /usr/local/include
brew link boost
sudo easy_install cmake
sudo pip install dlib

Make sure to download and extract shape_predictor_68_face_landmarks.dat.zip into the project directory!
http://sourceforge.net/projects/dclib/files/dlib/v18.10/shape_predictor_68_face_landmarks.dat.bz2


Run using 'python main.py'
