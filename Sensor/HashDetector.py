import cv2
import numpy as np

class HashDetector:
    def __init__(self) -> None:
        self.east_hash = self.image_to_hash(cv2.imread('EWSN/E.png'))
        self.west_hash = self.image_to_hash(cv2.imread('EWSN/W.png'))
        self.north_hash = self.image_to_hash(cv2.imread('EWSN/N.png'))
        self.south_hash = self.image_to_hash(cv2.imread('EWSN/S.png'))
    
    @staticmethod
    def image_to_hash(img : np.ndarray) -> list:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (16, 16))
        avg = gray.mean()
        bin = 1 * (gray > avg)
        return bin
    
    @staticmethod
    def hamming_distance(src_hash : list, cmp_hash : list) -> int:
        src_hash = src_hash.reshape(1,-1)
        cmp_hash = cmp_hash.reshape(1,-1)
        # 같은 자리의 값이 서로 다른 것들의 합
        distance = (src_hash != cmp_hash).sum()
        return distance
    
     
    def detect_direction_hash(self, img : np.ndarray) -> str:
        img_hash = self.image_to_hash(img)
        direction_list = ['E', 'W', 'S', 'N']
        hash_list = [self.east_hash, self.west_hash, self.south_hash, self.north_hash]
        hdist_list = []
        
        for hash in hash_list:
            hdist_list.append(self.hamming_distance(img_hash, hash))
            
        result = hdist_list.index(min(hdist_list))
        
        return direction_list[result]
        
if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    hashDetector = HashDetector()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        cv2.imshow('frame', frame)
        
        print(hashDetector.detect_direction_hash(frame))
        
        if cv2.waitKey(1) == 27:
            break
        
    cv2.destroyAllWindows()