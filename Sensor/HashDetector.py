import cv2
import os
import numpy as np
import glob

class HashDetector:
    def __init__(self, file_path) -> None:        
        self.directions_hash = []
        self.directions = []
        self.check_file_type(file_path)
        self.file_lst = os.listdir(file_path)
        if '.DS_Store' in self.file_lst:
            self.file_lst.remove('.DS_Store')
        for direction in self.file_lst:
            self.directions_hash.append(self.image_to_hash(cv2.imread(file_path + direction)))
            self.directions.append(direction.rsplit('.')[0])
        print(file_path + direction)
        print(self.directions)
         
    @staticmethod
    def image_to_hash(img : np.ndarray) -> list:        
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (16, 16))
        avg = img.mean()
        bin = 1 * (img > avg)
        return bin
    
    @staticmethod
    def hamming_distance(src_hash : list, cmp_hash : list, threshold : float = 0.1) -> int:
        src_hash = src_hash.reshape(1,-1)
        cmp_hash = cmp_hash.reshape(1,-1)
        # 같은 자리의 값이 서로 다른 것들의 합
        distance = (src_hash != cmp_hash).sum()
        return distance / (16 * 16)
    
    @staticmethod
    def check_file_type(image_folder_path, allowed_extensions=None):
        if allowed_extensions is None:
            allowed_extensions = ['.jpg', '.png', '.jpeg']
        no_files_in_folder = len(glob.glob(image_folder_path+"/*")) 
        extension_type = ""
        no_files_allowed = 0
        for ext in allowed_extensions:
          no_files_allowed = len(glob.glob(image_folder_path+"/*"+ext))
          if no_files_allowed > 0:
            extension_type = ext
            break
        assert no_files_in_folder == no_files_allowed, "The extension in the folder should all be the same, but found more than one extensions"
        return extension_type

    def detect_alphabet_hash(self, img : np.ndarray, threshold=0.3) -> str:
        img_hash = self.image_to_hash(img)
        hdist_dict = {}
        
        for i in range(len(self.directions)):
            direction = self.directions[i]
            hash = self.directions_hash[i]
            hdist_dict[direction] = self.hamming_distance(img_hash, hash)
        
        result = min(hdist_dict.keys(), key=(lambda k:hdist_dict[k]))
        
        if hdist_dict[result] > threshold:
            return None
        
        return result


if __name__ == "__main__":
    from Sensor.ImageProcessor import ImageProcessor
    from imutils import auto_canny
    from Sensor.Target import Target
    imageProcessor = ImageProcessor(video_path='src/S.h264')
    hashDetector = HashDetector(file_path='EWSN/')
    while True:
        targets = []
        src = imageProcessor.get_image()
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        mask = auto_canny(mask)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            approx = cv2.approxPolyDP(cnt, cv2.arcLength(cnt, True)*0.02, True)
            vertice = len(approx)

            if vertice == 4 and cv2.contourArea(cnt)> 2500:
                targets.append(Target(contour=cnt))
        if targets:
            targets.sort(key= lambda x: x.get_area)
            roi = targets[0].get_target_roi(src = src, pad=0, visualization=True)
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            cv2.imshow("roi thresh", mask)
            cv2.waitKey(1)
            print(hashDetector.detect_alphabet_hash(mask))
