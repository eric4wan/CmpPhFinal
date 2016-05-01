# CmpPhFinal


Written on Python 2.7.11


As far as we can tell, OSX seems to require the following commands:

brew install boost --with-python
brew install boost-python
sudo chown -R $USER:admin /usr/local/include
brew link boost
sudo easy_install cmake
sudo pip install dlib

Make sure to extract shape_predictor_68_face_landmarks.dat.zip into the project directory!

Run using 'python main.py'
