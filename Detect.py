import cv2 as cv
import numpy as np
import copy
import math
import Edges
import INTPoint

eps = 1e-7
votes = {}
Groups = []
VPoints = []
Centers = []
Cluster = []
voters = {}
def getEdges(image):
    #moved to Edges.py
    return Edges.getEdges(image)

def getLines(edges):
    #moved to Edges.py
    return Edges.getLines(edges)

def checkRound(pos,edges):
    #moved to Edges.py
    return Edges.checkRound(pos,edges)

def outOfSize(pos,edges):
    #moved to Edges.py
    return Edges.outOfSize(pos,edges)

def extenLine(line,edges):
    #moved to Edges.py
    return Edges.extenLine(line,edges)

def extenLines(lines,edges):
    #moved to Edges.py
    return Edges.extenLines(lines,edges)

def shouldMerge(line1,line2):
    #moved to Edges.py
    return Edges.shouldMerge(line1,line2)

def mergeLines(lines):
    #moved to Edges.py
    return Edges.mergeLines(lines)

def getLineABC(line):
    #moved to Edges.py
    return Edges.getLineABC(line)

def getCirAnch(a,b):
    #moved to Edges.py
    return Edges.getCirAnch(a,b)

def getCrossPoint(linea,lineb):
    #moved to INTPoint.py
    return INTPoint.getIntersectPoint(linea,lineb)

def sortLines(lines):
    #moved to Edges.py
    return Edges.sortLines(lines)

def getVPoints2(lines,arange = 0.2617):
    #moved to INTPoint.py
    global VPoints
    VPoints = INTPoint.getVPoints2(lines,arange)
    return VPoints

def getVPoints(num = 16):
    #this function is fallen into disuse because of the low speed
    for i in range(0,num + 1,1):
        lens = len(Groups[i])
        for j in range(0,lens,1):
            for k in range(j+1,lens,1):
                VPoints.append(getCrossPoint(Groups[i][j],Groups[i][k]))

def removeSame(list):
    #moved to INTPoint.py
    return INTPoint.removeSame(list)

def getLinesLength(line):
    #moved to INTPoint.py
    return INTPoint.getLinesLength(line)

def getMidPoint(line):
    #moved to INTPoint.py
    return INTPoint.getMidPoint(line)

def getArch(line,point):
    #moved to INTPoint.py
    return INTPoint.getArch(line,point)

def voteForPoint(lines):
    #moved to INTPoint.py
    global votes
    global voters
    votes,voters = INTPoint.voteForPoint(lines,VPoints)
    return

def getGraPoint(points):
    count = 1.0
    sumx = 0.0
    sumy = 0.0
    for point in points:
        w = votes[point]
        count += w
        sumx += w * point[0]
        sumy += w * point[1]
    return (sumx/count,sumy/count)

def devideIntoPoints(Points):
    global Cluster
    lens = len(Cluster)
    for i in range(0,lens,1):
        Cluster[i] = []
    
    for point in Points:
        if point[0] == 'p' or point[0] == 'h' or point[0] == 'v':
            continue
        if votes[point] == 0:
            continue
        minlens = 1e15
        minpos = 0
        now = -1
        for cen in Centers:
            now += 1
            lens = getLinesLength((point[0],point[1],cen[0],cen[1]))
            if lens < minlens:
                minlens = lens
                minpos = now
        Cluster[minpos].append(point)

def KMean(points,K = 3,step = 50):
    global Cluster
    global Centers
    Cluster = []
    Centers = []
    if K == 1:
        step = 1
    for i in range(0,K,1):
        Cluster.append([])
        Centers.append([0,0])
    
    count = 0
    for point in points:
        if point[0] != 'p' and point[0] != 'v' and point[0] != 'h' and votes[point] != 0:
            Centers[count][0] = point[0]
            Centers[count][1] = point[1]
            count += 1
        if count == K:
            break

    for i in range(0,step,1):
        devideIntoPoints(points)
        for i in range(0,K,1):
            Centers[i] = getGraPoint(Cluster[i])

def getFinal(points):
    count = 0.0
    num = 0
    p1 = 0.0
    ret1 = []
    p2 = 0.0
    ret2 = []
    for item in votes:
        if item[0] == 'p' or item[0] == 'h' or item[0] == 'v':
            if votes[item] > p1:
                p2 = p1
                ret2 = ret1
                p1 = votes[item]
                ret1 = item
            else:
                if votes[item] > p2:
                    p2 = votes[item]
                    ret2 = item
        else:
            count += votes[item]
            num += 1
    K = 3
    ret = []
    count = count / num * 0.1
    if p1 > count:
        K -= 1
        ret.append(ret1)
    if p2 > count:
        K -= 1
        ret.append(ret2)
    KMean(points,K)
    for i in range(0,K,1):
        ret.append(Centers[i])
    return ret

def deal(inputname,outputname):
    global votes
    global Groups
    global VPoints
    global Centers
    global Cluster
    global voters
    votes = {}
    Groups = []
    VPoints = []
    Centers = []
    Cluster = []
    voters = {}
    image = cv.imread(inputname)
    edges = getEdges(image)
    cv.imwrite(outputname + 'edges.jpg',edges)
    lines = getLines(edges)
    lines2 = copy.deepcopy(lines)
    lines2 = extenLines(lines2,edges)
    lines2 = mergeLines(lines2)

    #devideIntoGroups(lines2,3)
    lines2 = sortLines(lines2)
    getVPoints2(lines2)

    VPoints = removeSame(VPoints)
    voteForPoint(lines2)
    votes2 = sorted(votes.iteritems(),key=lambda votes:votes[1],reverse=True)
    lenofvotes = min(len(votes2),max(5,int(len(votes2) * 0.2)))
    votesFinal = {}
    VPoints = []
    for i in range(0,lenofvotes,1):
        votesFinal[votes2[i][0]] = votes2[i][1]
        VPoints.append(votes2[i][0])
    for i in range(lenofvotes,len(votes2),1):
        if votes2[i][0][0] == 'h' or votes2[i][0][0] == 'v' or votes2[i][0][0] == 'p':
            votesFinal[votes2[i][0]] = votes2[i][1]
            VPoints.append(votes2[i][0])
    votes = votesFinal
    ans = getFinal(VPoints)
    print ans
    edges = cv.cvtColor(edges,cv.COLOR_GRAY2BGR)
    edges2 = copy.deepcopy(edges)
    for item in lines:
        if item[0] == 'N':
            continue
        cv.line(edges,(item[0],item[1]),(item[2],item[3]),(0,0,255),2)
    for item in lines2:
        cv.line(edges2,(item[0],item[1]),(item[2],item[3]),(0,0,255),2)
    color = [255,0,0,0]
    for clu in Cluster:
        for i in range(0,4,1):
            if color[i] == 255:
                color[i+1] = 255
                color[i] = 0
                break
        for point in clu:
            if point[0] > 0 and point[1] > 0:
                if point[0] < edges.shape[1] and point[1] < edges.shape[0]:
                    if votes[point] == 0:
                        continue
                    cv.line(edges2,(int(point[0]),int(point[1])),(int(point[0]),int(point[1])),(color[1],color[2],color[3]),10)
    for point in ans:
        if point[0] > 0 and point[1] > 0:
            if point[0] < edges.shape[1] and point[1] < edges.shape[0]:
                cv.line(edges2,(int(point[0]),int(point[1])),(int(point[0]),int(point[1])),(255,255,255),10)

    cv.imwrite(outputname + 'linedetect.jpg',edges)
    cv.imwrite(outputname + 'answer.jpg',edges2)
    fd = open(outputname + 'answer.txt','w')
    fd.write('(' + str(ans[0][0]) + ',' + str(ans[0][1]) + ')(' + str(ans[1][0]) + ',' + str(ans[1][1]) + ')(' + str(ans[2][0]) + ',' + str(ans[2][1]) + ')')
    fd.close

deal("data/1.jpg",'1')