import cv2 as cv
import numpy as np
import copy
import math
import Edges


def drawLines(image,lines,color = (0,0,255),width = 2):
    for item in lines:
        cv.line(image,(item[0],item[1]),(item[2],item[3]),color,width)
    return image

image = cv.imread("data/3.jpg")
edges = Edges.getEdges(image)
lines = Edges.getLines(edges,20)
lines = Edges.extenLines(lines,edges)
lines = Edges.mergeLines(lines)
edges = cv.cvtColor(edges,cv.COLOR_GRAY2BGR)
image = drawLines(edges,lines)
cv.imwrite('test.jpg',image)
