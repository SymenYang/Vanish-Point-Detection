import cv2 as cv
import numpy as np
import copy
import math

eps = 1e-7

def getEdges(image):
    blur = cv.bilateralFilter(image,9,75,75)
    gray = cv.cvtColor(blur,cv.COLOR_BGR2GRAY)
    #blur2 = cv.GaussianBlur(gray,(5,5),0)
    edges = cv.Canny(gray,50,200,apertureSize = 3)
    return edges

def getLines(edges,minlength = 30):
    lines = cv.HoughLinesP(edges,1,np.pi/180,80,20,10)
    count = 0
    ret = []
    for t in lines:
        x1 = t[0][0]
        x2 = t[0][2]
        y1 = t[0][1]
        y2 = t[0][3]
        if (x2 - x1) ** 2 + (y2 - y1) ** 2 <= minlength ** 2:
            count += 1
            continue
        ret.append((x1,y1,x2,y2))
    return ret

def checkRound(pos,edges):
    patx = [-1,1,0,0,-1,1,-1,1]
    paty = [0,0,-1,1,-1,-1,1,1]
    x = pos[1]
    y = pos[0]
    for i in range(0,8):
        if outOfSize((y + paty[i],x + patx[i]),edges):
            continue
        if edges[x + patx[i]][y + paty[i]] == 255:
            return True
    return False

def outOfSize(pos,edges):
    return pos[1] < 0 or pos[1] >= edges.shape[0] or pos[0] < 0 or pos[0] >= edges.shape[1]

def extenLine(line,edges):
    x1 = line[0]
    y1 = line[1]
    x2 = line[2]
    y2 = line[3]
    
    dx = x2 - x1
    dy = y2 - y1
    nowx = x2
    nowy = y2 * 1.0
    sy = 0
    if dy > 0:
        sy = 1
    else:
        sy = -1
    if dx > 0:
        sx = 1
    else:
        sx = -1
    
    if dx == 0:
        while not outOfSize((nowx,int(nowy + sy)),edges):
            nowy += sy
            if checkRound((nowx,int(nowy)),edges):
                pass
            else:
                break
        retx2 = nowx
        rety2 = nowy
        nowx = x1
        nowy = y1
        while not outOfSize((nowx,int(nowy - sy)),edges):
            nowy -= sy
            if checkRound((nowx,int(nowy)),edges):
                pass
            else:
                break
        retx1 = nowx
        rety1 = nowy
        return [retx1,int(rety1),retx2,int(rety2)]

    k = float(dy) / dx
    while not outOfSize((nowx + sx,int(nowy + k)),edges):
        nowx += sx
        nowy += k
        if checkRound((nowx,int(nowy)),edges):
            pass
        else:
            break
    retx2 = nowx
    rety2 = nowy
    nowx = x1
    nowy = y1
    while not outOfSize((nowx - sx,int(nowy - k)),edges):
        nowx -= sx
        nowy -= k
        if checkRound((nowx,int(nowy)),edges):
            pass
        else:
            break
    retx1 = nowx
    rety1 = nowy
    return [retx1,int(rety1),retx2,int(rety2)]

def extenLines(lines,edges):
    ret = []
    for line in lines:
        extl = extenLine(line,edges)
        ret.append((extl[0],extl[1],extl[2],extl[3]))
    return ret

def getLineABC(line):
    x1 = line[0]
    x2 = line[2]
    y1 = line[1]
    y2 = line[3]
    if x2 < x1:
        tmp = x2
        x2 = x1
        x1 = tmp
        tmp = y2
        y2 = y1
        y1 = tmp
    
    c = 1
    if y1 * x2 == y2 * x1:
        c = 0
        b = 1.0
        a = -(b * y2 + c) / x2
        return a,b,c
    b = float(x1 - x2) / (y1*x2 - y2*x1)
    a = -(b * y2 + c) / x2
    if abs(a - 0) <= eps:
        a = 0
    if abs(b - 0) <= eps:
        b = 0
    if abs(a * x1 + b * y1 + c) - 0 >= eps or abs(a * x2 + b * y2 + c) - 0 >= eps:
        print (a * x1 + b * y1 + c,a * x2 + b * y2 + c)
        pass
    return a,b,c

def getCirAnch(a,b):
    if b == 0:
        return math.pi / 2
    else:
        return math.atan(a/(-b))

def sortLines(lines):
    tmp = {}
    for line in lines:
        index = (line[0],line[1],line[2],line[3])
        a,b,c, = getLineABC(line)
        data = getCirAnch(a,b)
        tmp[index] = data
    tmp = sorted(tmp.iteritems(),key=lambda tmp:tmp[1],reverse=False)
    ret = []
    for item in tmp:
        ret.append([item[0][0],item[0][1],item[0][2],item[0][3],item[1]])
    return ret

def disPoint2Line(point,line):
    x1 = line[0]
    y1 = line[1]
    x2 = line[2]
    y2 = line[3]

    x = point[0]
    y = point[1]

    dx1 = x - x1
    dy1 = y - y1
    dx2 = x2 - x1
    dy2 = y2 - y1
    
    dot = dx1 * dx2 + dy1 * dy2
    lens = math.sqrt(dx2 ** 2 + dy2 ** 2)
    ratio = float(dot)/(lens ** 2)
    if ratio < 0:
        ratio = 0
    if ratio > 1:
        ratio = 1
    cx = float(x1) + float(dx2) * ratio
    cy = float(y1) + float(dy2) * ratio
    dis = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) 
    return dis

def inLine(point,line,gap = 1):
    return disPoint2Line(point,line) <= gap

def shouldMerge(line1,line2):
    k1 = line1[4]
    k2 = line2[4]
    if abs(k1 - k2) >= 0.0175:
        if abs(k1 - k2) <= math.pi - 0.0174:
            return False
    Flag = False
    Flag = Flag or inLine((line1[0],line1[1]),line2)
    Flag = Flag or inLine((line1[2],line1[3]),line2)
    Flag = Flag or inLine((line2[0],line2[1]),line1)
    Flag = Flag or inLine((line2[2],line2[3]),line1)
    return Flag

def merge2Line(line1,line2):
    k = (line1[4] + line2[4]) / 2
    p = []
    p.append((line1[0],line1[1]))
    p.append((line1[2],line1[3]))
    p.append((line2[0],line2[1]))
    p.append((line2[2],line2[3]))
    lbP = [1000000,1000000]
    rtP = [-1000000,-1000000]
    for point in p:
        if lbP[0] > point[0] or (lbP[0] == point[0] and lbP[1] > point[1]):
            lbP[0] = point[0]
            lbP[1] = point[1]
        if rtP[0] < point[0] or (rtP[0] == point[0] and rtP[1] < point[1]):
            rtP[0] = point[0]
            rtP[1] = point[1]
    return (lbP[0],lbP[1],rtP[0],rtP[1],k)


def mergeLines(lines):
    lines = sortLines(lines)
    tmp = []
    used = []
    ret = []
    count = 0
    for i in range(0,len(lines),1):
        used.append(-1)
    for i in range(0,len(lines),1):
        now = used[i]

        if used[i] == -1:
            used[i] = count
            tmp.append([])
            tmp[count].append((lines[i],i))
            now = count
            count += 1
        print i
        for j in range(i+1,len(lines),1):
            if shouldMerge(lines[i],lines[j]):
                if used[j] == -1:
                    used[j] = now
                    tmp[now].append((lines[j],j))
                else:
                    target = used[j]
                    if target == now:
                        continue
                    for item in tmp[target]:
                        tmp[now].append(item)
                        used[item[1]] = now
                    tmp[target] = []

    for i in range(0,len(tmp),1):
        if len(tmp[i]) == 0:
            continue
        final = tmp[i][0][0]
        for j in range(1,len(tmp[i]),1):
            final = merge2Line(final,tmp[i][j][0])
        ret.append(final)
    return ret