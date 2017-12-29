#tutorial from https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/

# import the necessary packages
import numpy as np
import argparse
import imutils
import glob
import cv2

def match(image_template, source_path):
    template = cv2.imread(image_template) # loads image
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) # convert to grayscale
    template = cv2.Canny(template, 50, 200) # detects edges???
    (tH, tW) = template.shape[:2]
    cv2.imshow("Template", template)
    # idk if this will work for our circular images but we'll try

    image = cv2.imread(source_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found = None

    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        resized = imutils.resize(image, width = int(image.shape[1] * scale))
        r = image.shape[1] / float(resized.shape[1])

        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        edged = cv2.Canny(resized, 50, 200)
        result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

        # draw a bounding box around the detected region
        clone = np.dstack([edged, edged, edged])
        cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
        cv2.imshow("Visualize", clone)
        cv2.waitKey(0)

        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)

    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
    cv2.imshow("Image", image)
    cv2.waitKey(0)