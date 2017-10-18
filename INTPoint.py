import cv2 as cv
import numpy as np
import copy
import math
import Edges
eps = 1e-7


def getIntersectPoint(linea,lineb):
    a1,b1,c1 = Edges.getLineABC(linea)
    a2,b2,c2 = Edges.getLineABC(lineb)
    if abs(abs(a2/b2) - 1.0) < eps:
        pass
    if a2 != 0 and b2 != 0:
        if abs(a1/a2 - b1/b2) <= eps:
            return ('p',a2/b2)
    else:
        if a2 == 0 and b2 == 0:
            pass
        if a1 == 0 and a2 == 0:
            return ('h','h')
        if b1 == 0 and b2 == 0:
            return ('v','v')
    if abs(Edges.getCirAnch(a1,b1) - Edges.getCirAnch(a2,b2)) <= 0.03:
        return ('n','n')
    try:
        y = (1 - float(a2)/a1) / ((b1 * float(a2) / a1) - b2)
        x = (-y * b1 - 1) / a1
    except:
        return('n','n')
    return (int(x),int(y))

def getVPoints2(lines,arange = 0.2617):
    l = 0
    r = 0
    ret = []
    for i in range(0,len(lines),1):
        while (lines[r][4] - lines[i][4] <= arange and r < len(lines) - 1):
            r += 1
        while (lines[i][4] - lines[l][4] >= arange):
            l += 1
        for j in range(l,r,1):
            if j == i:
                continue
            ret.append(getIntersectPoint(lines[i],lines[j]))
    return ret

def removeSame(list):
    dic = {}
    ret = []
    flag = False
    for item in list:
        if item[0] == 'n':
            flag = True
        tmp = (item[0],item[1])
        if dic.has_key(tmp):
            continue
        dic[tmp] = 1
        ret.append(tmp)
    if flag:
        ret.remove(('n','n'))
    return ret

def getLinesLength(line):
    return math.sqrt((line[3] - line[1]) ** 2 + (line[2] - line[0]) ** 2)

def getMidPoint(line):
    return ((line[0] + line[2]) / 2,(line[1] + line[3]) / 2)

def getArch(line,point):
    Mid = getMidPoint(line)
    dx = line[0] - Mid[0]
    dy = line[1] - Mid[1]
    px = point[0] - Mid[0]
    py = point[1] - Mid[1]
    dot = dx*px + dy * py
    lens = math.sqrt(dx ** 2 + dy ** 2)
    lens2 = math.sqrt(px ** 2 + py ** 2)
    mir = dot / lens
    cos = abs(mir / lens2)
    if abs(cos) > 1:
        cos = float(int(cos))
    arch = math.acos(cos)
    return arch

def voteForPoint(lines,VPoints):
    votes = {}
    voters = {}
    for p in VPoints:
        votes[p] = 0.0
        voters[p] = 0
    for line in lines:
        a,b,c = Edges.getLineABC(line)
        lens = getLinesLength(line)
        for p in VPoints:
            if p == (387,77):
                pass
            if p[0] == 'h':
                if a == 0:
                    votes[p] += lens
                    voters[p] += 1
                continue
            if p[0] == 'v':
                if b == 0:
                    votes[p] += lens
                    voters[p] += 1
                continue
            if p[0] == 'p':
                if abs(a/b-p[1]) < eps:
                    votes[p] += lens
                    voters[p] += 1
                continue
            arch = getArch(line,p)
            if arch >= math.pi/18:
                continue
            votes[p] += lens * math.exp(-( arch / ( 2 * (0.1 ** 2 ) ) ) )
            voters[p] += 1
    for item in votes:
        if voters[item] <= 4:
            votes[item] = 0
    return votes,voters