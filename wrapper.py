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

def dealAImage(inputname,outputname,Oedges = False,Olines = False,OExLines = False,Oclassfy = True,Ostandard = True):
    image = cv.imread(inputname + '.jpg')
    orEdges = Edges.getEdges(image)
    print "got edges"
    orLines = Edges.getLines(orEdges,20)
    print "got lines , num : " + str(len(orLines))
    exLines = Edges.extenLines(orLines,orEdges)
    print "extend lines"
    exLines = Edges.mergeLines(exLines)
    print "merged lines"

    lines = copy.deepcopy(exLines)
    ans = [('a',0),('a',0),('a',0)]
    anslines = [[],[],[]]
    ansnum = -1
    ans[0],lines,anslines[0] = Clustering.getAnCenter(lines)
    print "first vanish point"
    if lines != None:
        ans[1],lines,anslines[1] = Clustering.getAnCenter(lines)
    print "second vanish point"
    if lines != None:
        ans[2],lines,anslines[2] = Clustering.getAnCenter(lines)
    print "third vanish point"
    for i in range (0,3,1):
        if ans[i] != None:
            ansnum = i
        else:
            break
    if Oedges:
        cv.imwrite(outputname + "_edges.jpg",orEdges)
    if Olines:
        image_lines = copy.deepcopy(image)
        drawLines(image_lines,orLines)
        cv.imwrite(outputname + "_lines.jpg",image_lines)
    if OExLines:
        image_ExLines = copy.deepcopy(image)
        drawLines(image_ExLines,exLines)
        cv.imwrite(outputname + "_exLines.jpg",image_ExLines)
    
    image_classfy = copy.deepcopy(image)
    if Oclassfy:
        if ansnum >= 0:
            image_classfy = drawLines(image_classfy,anslines[0],(255,255,0))
        if ansnum >= 1:
            image_classfy = drawLines(image_classfy,anslines[1],(0,255,255))
        if ansnum >= 2:
            image_classfy = drawLines(image_classfy,anslines[2],(255,0,255))
    else:
        image_classfy = drawLines(image_classfy,exLines)
    if Ostandard:
        fd = open(outputname + 'answer.txt','w')
        if ansnum >= 0:
            image_classfy = drawPoints(image_classfy,[ans[0]],(255,255,0))
            fd.write(" ( " + str(ans[0][0]) + ' , ' + str(ans[0][1]) + ' ) ')
        if ansnum >= 1:
            image_classfy = drawPoints(image_classfy,[ans[1]],(0,255,255))
            fd.write(" ( " + str(ans[1][0]) + ' , ' + str(ans[1][1]) + ' ) ')
        if ansnum >= 2:
            image_classfy = drawPoints(image_classfy,[ans[2]],(255,0,255))
            fd.write(" ( " + str(ans[2][0]) + ' , ' + str(ans[2][1]) + ' ) ')
        fd.close()
    cv.imwrite(outputname + "_final.jpg",image_classfy)
