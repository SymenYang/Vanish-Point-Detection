import cv2 as cv
import numpy as np
import copy
import math
import Edges
import INTPoint

eps = 1e-7

def filterVotes(votes,ratio = 0.8,minnum = 5):
    votes2 = sorted(votes.iteritems(),key=lambda votes:votes[1],reverse=True)
    lenofvotes = min(len(votes2),max(minnum,int(len(votes2) * ratio)))
    votesFinal = {}
    for i in range(0,lenofvotes,1):
        votesFinal[votes2[i][0]] = votes2[i][1]
    for i in range(lenofvotes,len(votes2),1):
        if votes2[i][0][0] == 'h' or votes2[i][0][0] == 'v' or votes2[i][0][0] == 'p':
            votesFinal[votes2[i][0]] = votes2[i][1]
    return votesFinal

def getGraPoint(cluster):
    if len(cluster) == 0:
        return ()
    count = 0.0
    sumx = 0.0
    sumy = 0.0
    for point in cluster:
        w = point[2]
        count += w
        sumx += w * point[0]
        sumy += w * point[1]
    return (sumx/count,sumy/count,count)

def getMaxPoint(cluster):
    if len(cluster) == 0:
        return ()
    maxdata = 0.0
    maxx = 0
    maxy = 0
    for point in cluster:
        w = point[2]
        if point > maxdata:
            maxdata = point
            maxx = point[0]
            maxy = point[1]
    return (maxx,maxy,maxdata)

def getCluster(votesdict,arange = 100,Max = False):
    votes = []
    ret = []
    for p in votesdict:
        if p[0] == 'h' or p[0] == 'p' or p[0] == 'v':
            ret.append((p[0],p[1],votesdict[p]))
            continue
        votes.append((p[0],p[1],votesdict[p]))
    clunum = []
    clusters = []
    for p in votes:
        clunum.append(-1)
        clusters.append([])
    count = 0
    for i in range(0,len(votes),1):
        now = clunum[i]
        if clunum[i] == -1:
            now = count
            count += 1
            clusters[now].append((votes[i][0],votes[i][1],votes[i][2],i))#(x,y,votes,pos)
            clunum[i] = now
        
        for j in range(i+1,len(votes),1):
            if INTPoint.getLinesLength((votes[i][0],votes[i][1],votes[j][0],votes[j][1])) <= arange:
                if clunum[j] == -1:
                    clunum[j] = now
                    clusters[now].append((votes[j][0],votes[j][1],votes[j][2],j))
                else:
                    if clunum[j] == now:
                        continue
                    target = clunum[j]
                    if len(clusters[target]) > len(clusters[now]):
                        tmp = target
                        target = now
                        now = tmp
                    for item in clusters[target]:
                        clunum[item[3]] = now
                        clusters[now].append(item)
                    clusters[target] = []

    for cluster in clusters:
        if len(cluster) == 0:
            continue
        if Max:
            ret.append(getMaxPoint(cluster))
        else:
            ret.append(getGraPoint(cluster))
    ret.sort(cmp=lambda x,y:cmp(x[2],y[2]),reverse = True)
    return ret

def removeBelongingLines(lines,point,arange = math.pi / 18):
    ret = []
    belong = []
    for line in lines:
        flag = True
        if point[0] == 'v':
            if abs(line[4] - math.pi/2)<= eps or abs(line[4] + math.pi / 2) <= eps:
                flag = False
        if point[0] == 'h':
            if abs(line[4] - 0) <= eps:
                flag = False 
        if point[0] == 'p':
            if line[2] - line[0] == 0:
                pass
            else:
                k = (line[3] - line[1]) / (line[2] - line[0])
                flag = not (k == point[1])
        if point[0] != 'h' and point[0] != 'v' and point[0] != 'p':
            arch = INTPoint.getArch(line,point)
            if arch <= arange:
                flag = False
        if flag:
            ret.append(line)
        else:
            belong.append(line)
    return ret,belong

def getAnCenter(lines,filter = 0.8):
    VPoints = INTPoint.getVPoints2(lines)
    print "got vote points : " + str(len(VPoints))
    votes,voters = INTPoint.voteForPoint(lines,VPoints)
    print "voted"
    votes = filterVotes(votes,0.8)
    centers = getCluster(votes,50)
    print "got clusters : " + str(len(centers))
    if centers == []:
        return None,None,None
    lines,anslines = removeBelongingLines(lines,centers[0])
    print "removed belonging lines"
    return centers[0],lines,anslines