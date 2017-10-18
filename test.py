import cv2 as cv
import numpy as np
import copy
import math
import Edges
import INTPoint
import Clustering

def drawLines(image,lines,color = (0,0,255),width = 2):
    for item in lines:
        cv.line(image,(item[0],item[1]),(item[2],item[3]),color,width)
    return image

def drawPoints(image,points,color = (255,0,0),width = 10):
    for point in points:
        if point[0] > 0 and point[1] > 0:
            if point[0] < image.shape[1] and point[1] < image.shape[0]:
                cv.line(image,(int(point[0]),int(point[1])),(int(point[0]),int(point[1])),color,width)
    return image

image = cv.imread("data/1.jpg")
edges = Edges.getEdges(image)
lines = Edges.getLines(edges,20)
lines = Edges.extenLines(lines,edges)
lines = Edges.mergeLines(lines)
VPoints = INTPoint.getVPoints2(lines)
votes,voters = INTPoint.voteForPoint(lines,VPoints)
votes = Clustering.filterVotes(votes,0.8)
centers = Clustering.getCluster(votes,100)
edges = cv.cvtColor(edges,cv.COLOR_GRAY2BGR)
image = drawLines(edges,lines)
image = image#drawPoints(image,votes,(0,0,255))
image = drawPoints(image,centers[0:3],(255,255,255))
print (centers[0:3])
cv.imwrite('test.jpg',image)
