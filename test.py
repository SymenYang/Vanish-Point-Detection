import cv2 as cv
import numpy as np
import copy
import math

eps = 1e-7
votes = {}
Groups = []
VPoints = []
Centers = []
Cluster = []
voters = {}
def getEdges(image):
    blur = cv.bilateralFilter(image,9,75,75)
    gray = cv.cvtColor(blur,cv.COLOR_BGR2GRAY)
    #blur2 = cv.GaussianBlur(gray,(5,5),0)
    edges = cv.Canny(gray,50,200,apertureSize = 3)
    return edges

def getLines(edges):
    lines = cv.HoughLinesP(edges,1,np.pi/3600,80,20,10)
    #lines = cv.HoughLines(edges,1,np.pi/1800,100)
    count = 0
    ret = []
    for t in lines:
        x1 = t[0][0]
        x2 = t[0][2]
        y1 = t[0][1]
        y2 = t[0][3]
        if (x2 - x1) ** 2 + (y2 - y1) ** 2 <= 900:
            count += 1
            continue
        ret.append([x1,y1,x2,y2])
    
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
        while not outOfSize((nowx,int(nowy)),edges):
            nowy += sy
            if checkRound((nowx,int(nowy)),edges):
                pass
            else:
                break
        retx2 = nowx
        rety2 = nowy
        nowx = x1
        nowy = y1
        while not outOfSize((nowx,int(nowy)),edges):
            nowy -= sy
            if checkRound((nowx,int(nowy)),edges):
                pass
            else:
                break
        retx1 = nowx
        rety1 = nowy
        return [retx1,int(rety1),retx2,int(rety2)]

    k = float(dy) / dx
    while not outOfSize((nowx,int(nowy)),edges):
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
    while not outOfSize((nowx,int(nowy)),edges):
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
    for line in lines:
        extl = extenLine(line,edges)
        line[0] = extl[0]
        line[1] = extl[1]
        line[2] = extl[2]
        line[3] = extl[3]
    return lines

def shouldMerge(line1,line2):
    d = 0.0
    for i in range(0,4,1):
        d += abs(line1[i] - line2[i])

    if d <= 25:
        return True
    return False

def mergeLines(lines):
    ret = []
    lens = len(lines)
    for i in range(0,lens,1):
        if lines[i][0] == 'N':
            continue
        for j in range(i+1,lens,1):
            if lines[j][0] == 'N':
                continue
            if shouldMerge(lines[i],lines[j]):
                lines[j][0] = 'N'
        ret.append((lines[i][0] , lines[i][1] , lines[i][2] , lines[i][3]))
    return ret
'''
def devideIntoGroups(lines,num = 16):
    for i in range(0,num + 1,1):
        Groups.append([])
    d = np.pi / num
    for line in lines:
        y = line[3] - line[1]
        x = line[2] - line[0]
        if x <= 0:
            if x == 0:
                y = abs(y)
            else:
                y = -y
                x = -x
        tan = float(y) / x
        if tan > 1e9:
            Groups[num].append([line[0],line[1],line[2],line[3]])
            continue
        arch = np.arctan(tan) + np.pi / 2
        group = int(math.floor(arch / d))
        if group >= num:
            pass
        Groups[group].append([line[0],line[1],line[2],line[3]])
'''
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

def getCrossPoint(linea,lineb):
    a1,b1,c1 = getLineABC(linea)
    a2,b2,c2 = getLineABC(lineb)
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

    if abs(getCirAnch(a1,b1) - getCirAnch(a2,b2)) <= 0.03:
        return ('n','n')
    try:
        y = (1 - float(a2)/a1) / ((b1 * float(a2) / a1) - b2)
        x = (-y * b1 - 1) / a1
    except:
        return('n','n')
    return (int(x),int(y))

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

def getVPoints2(lines,arange = 0.298):
    l = 0
    r = 0
    for i in range(0,len(lines),1):
        while (lines[r][4] - lines[i][4] <= arange and r < len(lines) - 1):
            r += 1
        while (lines[i][4] - lines[l][4] >= arange):
            l += 1
        for j in range(l,r,1):
            if j == i:
                continue
            VPoints.append(getCrossPoint(lines[i],lines[j]))

def getVPoints(num = 16):
    for i in range(0,num + 1,1):
        lens = len(Groups[i])
        for j in range(0,lens,1):
            for k in range(j+1,lens,1):
                VPoints.append(getCrossPoint(Groups[i][j],Groups[i][k]))

def removeSame(list):
    ret = []
    flag = False
    for item in list:
        if item[0] == 'n':
            flag = True
        tmp = [0,0]
        tmp[0] = item[0]
        tmp[1] = item[1]
        if tmp[0] == 'a':
            continue
        for i in range(0,len(list)):
            if i >= len(list):
                break
            if list[i][0] == tmp[0]:
                if list[i][0] == 'p':
                    if abs(list[i][1] - tmp[1]) < eps:
                        list[i] = ('a','a')
                else:
                    if list[i][1] == tmp[1]:
                        list[i] = ('a','a')
        ret.append((tmp[0],tmp[1]))
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

def voteForPoint(lines):
    for p in VPoints:
        votes[p] = 0.0
        voters[p] = 0
    for line in lines:
        a,b,c = getLineABC(line)
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
    lenofvotes = max(5,int(len(votes2) * 0.3))
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

for i in range(10,14,1):
    deal(str(i) + '.jpg',str(i))


#cv.namedWindow('image',cv.WINDOW_NORMAL)
#cv.imshow('image',edges)
#cv.waitKey(0)
#cv.destroyAllWindows()