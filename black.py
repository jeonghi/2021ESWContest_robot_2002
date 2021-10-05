import cv2
import numpy as np
import math

cap = cv2.VideoCapture("./Sensor/src/debug/black_area.h264")

def mask_color(src, color='YELLOW'):
    if color == 'YELLOW':
        #hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
        #h, l, s = cv2.split(hls)
        #ret, mask = cv2.threshold(s, 70, 255, cv2.THRESH_BINARY)
        #src = cv2.bitwise_and(src, src, mask=mask)
        match_lower = np.array([10, 40, 110])  # yellow_lower
        match_upper = np.array([50, 255, 255])  # yellow_upper

    if color == 'GREEN':
        hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
        h, l, s = cv2.split(hls)
        ret, mask = cv2.threshold(s, 70, 255, cv2.THRESH_BINARY)
        src = cv2.bitwise_and(src, src, mask=mask)
        match_lower = np.array([20, 20, 20])  # green_lower
        match_upper = np.array([80, 255, 255])  # green_upper

    if color == 'BLACK':
        #hls = cv2.cvtColor(src, cv2.COLOR_BGR2HLS)
        #h, l, s = cv2.split(hls)
        #ret, mask = cv2.threshold(s, 70, 255, cv2.THRESH_BINARY)
        #src = cv2.bitwise_and(src, src, mask=mask)
        match_lower = np.array([0, 0, 0])  # green_lower
        match_upper = np.array([255, 255, 30])  # green_upper
    
    src = cv2.GaussianBlur(src, (5, 5), 0)
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, match_lower, match_upper)
    return mask

while True:
    ret, src = cap.read()
    point_array = []
    if not ret:
        break
    hsv_image = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    val_S =0
    val_V = 0
    array = np.full(hsv_image.shape, (0, val_S, val_V), dtype=np.uint8)
    val_add_image = cv2.add(hsv_image, array)
    src = cv2.cvtColor(val_add_image, cv2.COLOR_HSV2BGR)
    result=mask_color(src, 'BLACK')

    #contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #print(len(contours))
    #contours_min = np.argmin(contours[0], axis = 0)
   # contours_max = np.argmax(contours[0], axis = 0)

  #  xMin = contours[0][contours_min[0][0]][0][0]
  #  yMin =contours[0][contours_min[0][1]][0][1]
  #  xMax = contours[0][contours_max[0][0]][0][0]
  #  yMax = contours[0][contours_max[0][1]][0][1]

 #   print("x-Min =", xMin)
 #   print("y-Min =", yMin)
  #  print("x-Max =", xMax)
  #  print("y-Max =", yMax)


    contours , _ = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contour = contours[0]

    # contour[:,:,0] 은 point의 x좌표 값만 포함하는 배열
    # contour[:,:,1] 은 point의 y좌표 값만 포함하는 배열
    # argmin() 을 적용하면 가장 작은 값의 위치가 나옴.
    # argmax() 을 적용하면 가장 높은 값의 위치가 나옴.
    # 찾은 위치를 다시 contour 에서 찾으면 됨.
    leftmost = tuple(contour[contour[:,:,0].argmin()][0])
    rightmost = tuple(contour[contour[:,:,0].argmax()][0])
    topmost = tuple(contour[contour[:,:,1].argmin()][0])
    bottommost = tuple(contour[contour[:,:,1].argmax()][0])

    print(leftmost)
    print(rightmost)
    print(topmost)
    print(bottommost)

    cv2.circle(src,leftmost,5,(0,0,255),-1)
    cv2.circle(src,rightmost,5,(0,0,255),-1)
    cv2.circle(src,topmost,5,(0,0,255),-1)
    cv2.circle(src,bottommost,5,(0,0,255),-1)

    #cv2.imshow("img",img)

    for cnt in contours:
        cv2.drawContours(src, cnt, -1, (255, 0, 0), 2)

    cv2.imshow("src", src)
    #cv2.imshow("gray", gray)
    cv2.imshow("result", result)
    if cv2.waitKey(10) == 27:
        break
cv2.destroyAllWindows()

        