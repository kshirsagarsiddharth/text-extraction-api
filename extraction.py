import cv2 
import numpy as np
import re 
import pytesseract 
from scipy import ndimage 
import os 


class Preprocessing:
    def __init__(self, image) -> None:
        self.image = image 
        self.ORIGINAL = image
    
    def correct_orientation(self): 
        rotation_data = pytesseract.image_to_osd(self.image) 
        rotation = re.findall('Rotate:\s\d+', rotation_data)[0] 
        #print(rotation) 
        degrees = 360 - int(rotation.split()[-1])
        self.image = ndimage.rotate(self.image, degrees)

    
    def get_grayscale(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) 
    
    def remove_noise(self): 
        self.image = cv2.medianBlur(self.image,5)
    
    def thresholding(self): 
        self.image = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    def dilate(self):
        kernel = np.ones((5,5), np.uint8) 
        self.image = cv2.dilate(self.image, kernel, iterations=1)
    
    def erode(self):
        kernel = np.ones((5,5), np.uint8) 
        self.image = cv2.erode(self.image, kernel, iterations=1)
    
    def opening(self): 
        kernel = np.ones((5,5), np.uint8) 
        self.image =  cv2.morphologyEx(self.image, cv2.MORPH_OPEN, kernel)

    def closing(self): 
        kernel = np.ones((5,5), np.uint8) 
        self.image =  cv2.morphologyEx(self.image, cv2.MORPH_OPEN, kernel)
    
    def canny(self):
        med_val = np.median(self.ORIGINAL) 
        lower = int(max(0, 0.7* med_val))
        upper = int(min(255,1.3 * med_val))
        self.image = cv2.Canny(image = self.image, threshold1= lower, threshold2=upper) 
    
    def extract_text(self): 
        return pytesseract.image_to_string(self.image)


    
    


    
