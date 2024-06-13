#! /usr/bin/env python

    
###INSTRUCTIONS###
print ("""

Numbers 1-5 toggle the terrain types for production with mouseclicks.
Number 6 toggles guy movement.  The guy will move 1 hex toward where you click.
Hitting 'h' will continue to move him along his path until he's reached his destination.
Number 7 prints a list of all the hex types.
Number 0 tests the distance formula.
y,g,b,n,j,u moves the guy N,NW,SW,S,SE,NE, respectively.
Hitting 'Enter' starts the growth process.  Hitting 'Enter' again will stop it.
m, finds the nearest meadow to where you are.

""")

import pdb

import random
import os

import pygame
from pygame.locals import *

import pygame.time

pygame.init()

#This determines the size of the map
#For Jim's screen, use 90, 43
#For my screen, use 47, 20
xinput = 90
yinput = 43

#This determines hex size
hexHeight = 24
hexWidth = 21
xAdj = 7

winsizex = hexWidth * xinput + 29
winsizey = hexHeight * yinput + 37

window = pygame.display.set_mode((winsizex, winsizey))
pygame.display.set_caption('Tooth Valley')
screen = pygame.display.get_surface()

#This is where I'll declare my variables
color = ['dirt','meadow','thicket','forest','oldForest', 'mountain', 'man','black','house','litHouse']
dirt,meadow,thicket,forest,oldForest,mountain,man,black,house,litHouse = range(0,10)
colorSurf = []
colorPath = []
allGuys = []
quitgame = False
nopick = False
inBounds = True
fire = True
forestFire = False
newColor = 0
hexAttribList = {}
go = False
path = []
gameTime = 0

hexagon = os.path.join("ImageFolder", "Hex.png")
greenhexagon = os.path.join("ImageFolder", "Hexclicked.png")
White = (255, 255, 255)
for c in color:
    colorPath = os.path.join("ImageFolder",c+".png")
    colorSurf.append(pygame.image.load(colorPath))

hexagon_surface = pygame.image.load(hexagon)

def longToShort(longx, longy):
    shortx = ((longx + 11)/hexWidth -1)
    if shortx % 2 == 0:
        shorty = longy/hexHeight
    else:
        shorty = (longy - (hexHeight/2))/hexHeight
    return (shortx, shorty)

def shortToLong(shortx, shorty):
    longx = shortx * hexWidth + 10
    if shortx % 2 == 0:
        longy = shorty * hexHeight
    else:
        longy = shorty * hexHeight + (hexHeight/2)
    return (longx, longy)

# These require short coordinates
def N(x, y):
    y -= 1
    return (x, y)

def NW(x, y):
    x -= 1
    if x % 2 == 1:
        y -= 1
    return (x, y)

def SW(x, y):
    x -= 1
    if x % 2 == 0:
        y += 1
    return (x, y)

def S(x, y):
    y += 1
    return (x, y)

def SE(x, y):
    x += 1
    if x % 2 == 0:
        y += 1
    return (x, y)

def NE(x, y):
    x += 1
    if x % 2 == 1:
        y -= 1
    return (x, y)


#This function decides in which hex a set of raw coordinates reside.
#This returns short coordinates.
def findHexClicked(rawx, rawy, nopick):
    ymid = 0
    xmid = 0
    if (rawx + 4) % hexWidth in range(0, 15):
        xmid = (rawx + xAdj) - (rawx + xAdj) % hexWidth + 3
        if (xmid - hexHeight)/hexWidth % 2 == 0:
            if rawy % hexHeight != 0:
                ymid = (rawy + hexHeight) - (rawy % hexHeight + (hexHeight/2))
            else:
                print ("line")
                nopick = True
        if (xmid - hexHeight)/hexWidth % 2 != 0:
            if (rawy - (hexHeight/2)) % hexHeight != 0:
                ymid = (rawy + 10) - (rawy + (hexHeight/2)) % hexHeight + 2
            else:
                print ("line")
                nopick = True
    else:
        ymid = rawy - rawy % (hexHeight/2)
        xmid = rawx - rawx % hexWidth + 3
        if (rawx + 11) % 42 in range(21, 29):
            if (rawy/(hexHeight/2)) % 2 == 0:
                if (rawx - 3) % xAdj + (rawy % (hexHeight/2))/2 > 6:
                    ymid += (hexHeight/2)
                    xmid += hexWidth
            if (rawy/(hexHeight/2)) % 2 != 0:
                if (rawx - 3) % xAdj + ((hexHeight/2) - (rawy %
                (hexHeight/2)))/2 < xAdj:
                    ymid += (hexHeight/2)
                if (rawx - 3) % xAdj + ((hexHeight/2) - (rawy %
                (hexHeight/2)))/2 > 6:
                    xmid += hexWidth
        if (rawx + 11) % 42 in range(0, 8):
            if (rawy/(hexHeight/2)) % 2 != 0:
                if (rawx - 3) % xAdj + (rawy % (hexHeight/2))/2 > 6:
                    ymid += (hexHeight/2)
                    xmid += hexWidth
            if (rawy/(hexHeight/2)) % 2 == 0:
                if (rawx - 3) % xAdj + ((hexHeight/2) - (rawy %
                (hexHeight/2)))/2 < xAdj:
                    ymid += (hexHeight/2)
                if (rawx - 3) % xAdj + ((hexHeight/2) - (rawy %
                (hexHeight/2)))/2 > 6:
                    xmid += hexWidth
    xblit = xmid - ((hexWidth + xAdj)/2)
    yblit = ymid - (hexHeight/2)
    if (xblit, yblit) == (0, 0):
        nopick = True
    if xmid < ((hexWidth + xAdj)/2):
        nopick = True
    if ymid < 20:
        nopick = True
    if xmid > (winsizex - 14):
        nopick = True
    if ymid > (winsizey - 20):
        nopick = True
    if nopick == False:
        (xblit, yblit) = longToShort(xblit, yblit)
        return (xblit, yblit)
    if nopick == True:
        print ("no pick")
        return (0,0)

#this blits a hex of a certain color to a specified location
def blitHex(shortx,shorty):
    (x, y) = shortToLong(shortx, shorty)
    if isInBounds(shortx,shorty):
        color = getHexType((shortx,shorty))
        color_surface = colorSurf[int(color)]
        color_surface.set_colorkey(White)
        screen.blit(color_surface, (x, y))
        numHouses = getNumHouses((shortx,shorty))
        numPeople = getNumPeople((shortx,shorty))
        if numHouses > 0 and numPeople > 0:
            blitHouse(shortx,shorty,litHouse)
        elif numHouses > 0:
            blitHouse(shortx,shorty,house)
        else:
            if numPeople > 0:
                blitMan(shortx,shorty,man)
        southy = (shorty + 1)
        if go == True and getNumPeople((shortx,southy)) > 0:
            blitHex(shortx,southy)
    else:
        color = black
        color_surface = colorSurf[int(color)]
        color_surface.set_colorkey(White)
        screen.blit(color_surface, (x, y))        

def blitHouse(shortx,shorty,color):
    (shortx,shorty) = (shortx,shorty)
    (x,y) = shortToLong(shortx, shorty)
    color_surface = colorSurf[int(color)]
    color_surface.set_colorkey(White)
    screen.blit(color_surface, (x, y))
    
def blitMan(shortx,shorty,color):
    (shortx,shorty) = (shortx,shorty)
    (x,y) = shortToLong(shortx, shorty)
    y-=2
    x+=8
    color_surface = colorSurf[int(color)]
    color_surface.set_colorkey(White)
    screen.blit(color_surface, (x, y))



#returns a list of tuple coordinates of the hexes next to a given coordinate
def findAdjct(x,y):
    (x,y) = (x,y)
    goodCoor = []
    xn,yn = N(x,y)
    xne,yne = NE(x,y)
    xse,yse = SE(x,y)
    xs,ys = S(x,y)
    xsw,ysw = SW(x,y)
    xnw,ynw = NW(x,y)
    allCoor = ((xn,yn),(xne,yne),(xse,yse),(xs,ys),(xsw,ysw),(xnw,ynw))
    for n in allCoor:
        (x,y) = n
        inBounds = isInBounds(x,y)
        if inBounds == True:
            goodCoor.append(n)
    return goodCoor

def adjctTo(hex1,hex2):
    adjctHexes = findAdjct(hex1[0], hex1[1])
    for n in adjctHexes:
        if n == hex2:
            return True
    return False
#returns True if it finds something, False if it doesn't.

def lookForSomething(nearHexes, something):
    cantFind = False
    foundSomething = False
    listFound = []
    for z in range(0,6):
        for n in nearHexes:
            if something == hexAttribList[n]:
                listFound.append(n)
                foundSomething = True
    if foundSomething == False:
        cantFind = True
        return foundSomething, cantFind, listFound

    #this disallows searching from mountains
    tempList = []
    for n in nearHexes:
        if mountain != hexAttribList[n]:
            tempList.append(n)
    nearHexes = tempList
    #END search disallow

    if len(nearHexes) > 0:
        return foundSomething, cantFind, nearHexes
    else:
        cantFind = True
        return foundSomething, cantFind, [(0,0),(0,0)]


def searchLoop(something,tryThese,blackList):
    tryThese2 = []
    for n in tryThese:
        newSet = findAdjct(n[0],n[1])
        for n in newSet:
            if n not in tryThese and n not in blackList and isInBounds(n[0],n[1]):
                if getHexType(n) != mountain or something == mountain:
                    tryThese2.append(n)

    return tryThese2,tryThese


def searchKind(something,curHex):
    if something in range(dirt,man):
        if something == getHexType(curHex):
            return True
        else:
            return False
    if something == house:
        if getNumHouses(curHex) > 0:
            return True
        else:
            return False

#returns a list of the closest given thing to a set of coordinates
def findNearest(something, curHex):
    distance = 0
    if searchKind(something,curHex):
        return [curHex],distance
    blackList = []
    tryThese = [curHex]
    goodHexes = []
    while len(goodHexes) == 0:
#        pdb.set_trace()
        if distance >= 20:
            return goodHexes,distance
        for n in tryThese:
            if n not in goodHexes:
                if searchKind(something,n):
                    goodHexes.append(n)
                elif something == forest and searchKind(oldForest,n):
                    goodHexes.append(n)
        if len(goodHexes) > 0:
            return goodHexes,distance
        tryThese,blackList = searchLoop(something,
                                tryThese,blackList)
        distance += 1

#findRealNearest takes more computation 
#but it takes terrain costs into consideration
def findRealNearest(something,curHex):
    bestHex,bestDist,bestPath = (0,0),1000,[]
    distance = 0
    if searchKind(something,curHex):
        return [curHex],distance, []
    blackList = []
    tryThese = [curHex]
    goodHexes = []
    maxDistance = 100
    while len(goodHexes) == 0:
        if distance >= maxDistance:
            return bestHex,bestDist,bestPath
        for n in tryThese:
            if n not in goodHexes:
                if searchKind(something,n):
                    goodHexes.append(n)
                elif something == forest and searchKind(oldForest,n):
                    goodHexes.append(n)
        if len(goodHexes) > 0:
            for n in goodHexes:
                path,traveled = findRoute(n,curHex)
                if traveled < bestDist:
                    bestDist = traveled
                    bestHex = n
                    bestPath = path
            goodHexes = []
            maxDistance = bestDist
        tryThese,blackList = searchLoop(something,
                                tryThese,blackList)
        distance += 1
    
    
    return bestHex,bestDist,bestPath

        
##################### THESE ARE FOR A* ###############################

#finds distance between two points as crow flies
def crowDist(start,end):
    (x1,y1) = start
    (x2,y2) = end
    distance = abs(x1 - x2) + abs(y1-y2)
    if x1 != x2 and y1!=y2:
        distance -= (1 + abs(x2-x1))/2
        if abs(x2 -x1) >= (2 * abs(y1 -y2)):
            distance = abs(x2-x1)
        else:
            if x2 > x1 and y2 < y1 and x1%2==1:
                distance += 1
            if x2 > x1 and y2 > y1 and x1%2==0 and x2%2==1:
                distance += 1
            if x2 < x1 and y2 < y1 and x1%2==1 and x2%2==0:
                distance += 1
            if x2 > x1 and y2 < y1 and x1%2==1 and x2%2==1:
                distance -= 1
            if x2 < x1 and y2 > y1 and x1%2==0 and x2%2==1:
                distance += 1

    return distance


def backTrackPath(curHex,start,nodesFromStart):
    path = [curHex]
    while start not in path:
        curHex = path[(len(path) -1)]
        value = nodesFromStart[curHex]
        adjctHexes = findAdjct[curHex[0],curHex[1]]
        for nextHex in adjctHexes:
            if nextHex in nodesFromStart and nodesFromStart[nextHex] < value:
                value = nodesFromStart[nextHex]
                bestHex = nextHex
        path.append(bestHex)
    tempList = []
    while len(path) > 0:
        tempList.append(path[(len(path) - 1)])
        del path[(len(path) - 1)]
    
    return tempList


#This decides whether or not to update the priority queue, and then updates accordingly
def addPriority(priorityQ,curHex,value,nodeValues):
    if len(priorityQ) == 0:
        priorityQ.append(curHex)
    else:
        if curHex in priorityQ:
            if nodeValues[curHex] <= value:
                return priorityQ,nodeValues
            else:
                for n in range(0,len(priorityQ)):
                    if priorityQ[n] == curHex:
                        del priorityQ[n]
                        break
    addedSomething = False
    for n in range(0,len(priorityQ)):
        if nodeValues[priorityQ[n]] > value:
            tempList = priorityQ[:n] + [curHex] + priorityQ[n:]
            priorityQ = tempList
            addedSomething = True
            break
    if addedSomething == False:
        priorityQ.append(curHex)
    nodeValues[curHex] = value
    return priorityQ,nodeValues

#updates all my various lists for a specific hex.
def updateValues(nextHex,priorityQ,nodeValues,nodesFromStart,nodesFromEnd,end,curHex):
    #This is where the travel costs for terrain are defined
    if hexAttribList[nextHex] == forest:
        travelCost = 2
    if hexAttribList[nextHex] == thicket:
        travelCost = 3
    else:
        travelCost = 1
    fromEnd = crowDist(nextHex,end)
    fromStart = (nodesFromStart[curHex] + travelCost)
    
    if nextHex not in nodeValues:
        nodesFromEnd[nextHex] = fromEnd
        nodesFromStart[nextHex] = fromStart

    elif nodesFromStart[nextHex] > fromStart:
        nodesFromStart[nextHex] = fromStart
    
    value = (fromEnd + nodesFromStart[nextHex])
    priorityQ,nodeValues = addPriority(priorityQ,nextHex,value,nodeValues)
    
    
    return priorityQ,nodeValues,nodesFromStart,nodesFromEnd

#This finds the optimal path between two points on the map
def findRoute(start,end):
    gotoMountain = False
    traveled = []
    blackList = []
    priorityQ = [start]
    distance = crowDist(start,end)
    nodeValues = {start:distance}
    nodesFromStart = {start:0}
    nodesFromEnd = {start:distance}
    goodPath = False

    while goodPath == False:
        curHex = priorityQ[0]
        traveled.append(curHex)
        adjctHexes = findAdjct(curHex[0],curHex[1])
        for nextHex in adjctHexes:
            if nextHex not in blackList:
                inBounds = True
                inBounds = isInBounds(nextHex[0], nextHex[1])
                if hexAttribList[nextHex] == mountain:
                    inBounds = False
                    if nextHex == end:
                        inBounds = True
                if inBounds == False:
                    blackList.append(nextHex)
            if nextHex not in blackList:
                priorityQ,nodeValues,nodesFromStart,nodesFromEnd = updateValues(
                    nextHex,priorityQ,nodeValues,nodesFromStart,nodesFromEnd,end,curHex)
        blackList.append(priorityQ[0])
        del priorityQ[0]

        if len(priorityQ) == 0:
            path = []
            return path,0
        if priorityQ[0] == end:
            goodPath = True

            path = backTrackPath(priorityQ[0],start,nodesFromStart)
            if hexAttribList[end] == mountain:
                del path[(len(path) -1 )]
    if end in nodesFromStart:
        return path, nodesFromStart[end]
    return path, 0


    
    

##########################################################################

#This moves coordinates one space in a random direction
def randomWalk(startx,starty,forestFire):
    (startx,starty) = (startx,starty)
    possible = [0,1,2,3,4,5]
    inBounds = False
    while inBounds == False:
        if len(possible) > 0:
            inBounds = True
            m = random.randint(0,(len(possible)-1))
            direction = possible[m]
            if direction == 0:
                newCoords = N(startx, starty)
            if direction == 1:
                newCoords = NE(startx, starty)
            if direction == 2:
                newCoords = SE(startx, starty)
            if direction == 3:
                newCoords = S(startx, starty)
            if direction == 4:
                newCoords = SW(startx, starty)
            if direction == 5:
                newCoords = NW(startx, starty)
            inBounds = isInBounds(newCoords[0], newCoords[1])
                       
            if inBounds == True:
                hexType = getHexType(newCoords) 
                if hexType > oldForest:
                    inBounds = False
            #This gives the resistences of various terrain to fire
                if forestFire:
                    
                    if hexType == dirt:
                        inBounds = False
                    if hexType == meadow:
                        x = random.randint(0,3)
                        if x != 3:
                            inBounds = False
                    if hexType == forest:
                        x = random.randint(0,3)
                        if x == 3:
                            inBounds = False
                    if hexType == oldForest:
                        x = random.randint(0,20)
                        if x != 20:
                            inBounds = False
                #END fire resistence
            if inBounds == False:
                del possible[m]
            if inBounds == True:
                return newCoords, inBounds
        if len(possible) == 0:
            return (startx, starty), inBounds




# This decides if a set of coordinates are in the bounds of the map
def isInBounds(x, y):
    inBounds = True
    if y > yinput:
        inBounds = False
    if x%2 == 1 and y > (yinput - 1):
        inBounds = False
    if x > (xinput - 1):
        inBounds = False
    if x < 0:
        inBounds = False
    if x%2==0 and y==0:
        inBounds = False
    if y < 0:
        inBounds = False
    return inBounds

#This does a random walk for a given set of coordinates and walk length
def walkCycle(x, y, minWalk, maxWalk, color,forestFire):
    size = random.randint(minWalk,maxWalk)
    while size > 0:
        (x2, y2), inBounds = randomWalk(x, y,forestFire)
        if inBounds == True:
            if color == 0 or color == 1:
                color = random.randint(0,4)
                if color > 1:
                    color = 1
            
            hexAttribList[(x2,y2)] = color
#            blitHex((x2,y2))
            (x,y)=(x2,y2)
            size -= 1
        else:
            size = 0
        setNumTrodden(x,y,0)
    pygame.display.flip()






def findRandomHex():
    inBounds = False
    while inBounds == False:
        randx = random.randint(0, xinput-1)
        randy = random.randint(0, yinput)
        inBounds = isInBounds(randx,randy)
    return(randx,randy)





def grow():
    randHex = findRandomHex()

    if (hexAttribList[randHex])%8 != mountain or dirt or oldForest:
        fire = random.randint(0, 50)
        if fire == 1:
            forestFire = True
            walkCycle(randHex[0], randHex[1], 999, 1000, 0,forestFire)
            forestFire = False
        else:
            checkGrowth = findAdjct(randHex[0],randHex[1])
            curType = (hexAttribList[randHex])%8
            canGrow = False

            if curType == forest:
                canGrow = True
                mountCount = 0
                for m in checkGrowth:
                    z = (hexAttribList[m])%8
                    if z == mountain:
                        mountCount += 1
                    if z < forest or z > mountain or mountCount > 1:
                        canGrow = False
                        break


            else:
                for m in checkGrowth:
                    z = (hexAttribList[m])%8
                    if z > curType or curType == dirt:
                        if curType < forest and z < mountain:
                            canGrow = True
                            break

            if canGrow == True:
                if getNumTrodden(randHex[0],randHex[1]) > 0:
                    canGrow = False
                    numTrodden = getNumTrodden(randHex[0],randHex[1])
                    setNumTrodden(randHex[0], randHex[1],numTrodden-1)

            goAgain = False
            if canGrow == True:
                hexAttribList[randHex] += 1
#                blitHex(randHex)
                if curType == dirt:
                    checkHexes = findAdjct(randHex[0],randHex[1])
                    addr = random.randint(0,(len(checkHexes)-1))
                    m = checkHexes[addr]
                    inBounds = isInBounds(m[0],m[1])
                    if (hexAttribList[m])%8 == dirt and inBounds:
                        hexAttribList[m] += meadow
#                        blitHex(m)

#    pygame.display.flip()

def terrainCost(hexAddr):
    terrain = (hexAttribList[hexAddr])%8
    if terrain == forest or oldForest:
        return 2
    if terrain == thicket:
        return 3
    else:
        return 1

def getHexType(curHex):
    return (hexAttribList[curHex]) % 8

def getNumHouses(curHex):
    return int((hexAttribList[curHex]%512)/64)

def getNumTrodden(x,y):
    return int(hexAttribList[(x,y)]/512)

def getNumPeople(curHex):
    return int((hexAttribList[curHex]%64)/8)

def setHexType(curHex,hexType):
    if hexType in range(0,8):
        oldHexType = getHexType(curHex)
        hexAttribList[curHex] += hexType - oldHexType

def setNumHouses(curHex,numHouses):
    if numHouses in range(0,8):
        oldNumHouses = getNumHouses(curHex)
        hexAttribList[curHex] += (numHouses - oldNumHouses) * 64

def setNumTrodden(x,y,numTrodden):
    if numTrodden in range(0,8):
        oldNumTrodden = getNumTrodden(x,y)
        hexAttribList[(x,y)] += (numTrodden - oldNumTrodden) * 512

def setNumPeople(curHex,numPeople):
    if numPeople in range(0,8):
        oldNumPeople = getNumPeople(curHex)
        hexAttribList[curHex] += (numPeople - oldNumPeople) * 8

#this creates a random map
def createMap():
    for xofhex in range(0, xinput):
        if xofhex % 2 == 0:
            for yofhex in range(1, yinput + 1):
                hexAttribList[(xofhex,yofhex)] = random.randint(0, 3)
#                blitHex((xofhex, yofhex))

        else:
            for yofhex in range(0, yinput):
                hexAttribList[(xofhex,yofhex)] = random.randint(0, 3)
#                blitHex((xofhex, yofhex))

   #This creates the mountains
    numMountains = (xinput * yinput)/50
    while numMountains > 0:
        randx = random.randint(0, xinput-1)
        randy = random.randint(1, yinput-1)
        walkCycle(randx, randy, 3, 7, mountain,forestFire)
        numMountains -= 1




class mobile:
    location = (0,0)
    home = (0,0)
###if exactly 2 nonhuman mobiles of the same type are at the home of 1 and not the other, then instantiate another of that type###
    jobs = []
    moveCost = {forest:2, meadow:1, dirt:1, oldForest:2, thicket:3}
    queueCount = 0
    priorityQueue = []
    myMap = {}

    #this will be the list of activities like ‘eat’,
    #‘sleep’, and ‘build stuff’ which will each call a function like my
    #Current ‘live’ function.  Once its done with the first item on the
    #list it should move to the next.  If it’s empty, repopulate according to need.

    def updatePriorityQueue(self,function):
        if function == 'Explore':
            self.exploreCount = random.randint(10,20)
        print (function)
#        pdb.set_trace()
        if function in self.priorityQueue:
            for n in range(0,len(self.priorityQueue)):
                if self.priorityQueue[n] == function:
                    del self.priorityQueue[n]
                    break
        self.priorityQueue.append(function)

    def searchLoop(self,something,tryThese,blackList):
        tryThese2 = []
        for n in tryThese:
            newSet = findAdjct(n[0],n[1])
            for n in newSet:
                if n not in tryThese and n not in blackList and isInBounds(n[0],n[1]) and n in self.myMap:
                    if getHexType(n) != mountain or something == mountain:
                        tryThese2.append(n)

        return tryThese2,tryThese


#returns a list of the closest given thing to a set of coordinates
    def findNearest(self, something, curHex):
        distance = 0
        if searchKind(something,curHex):
            return [curHex],distance
        blackList = []
        tryThese = [curHex]
        goodHexes = []
        while len(goodHexes) == 0:
    #        pdb.set_trace()
            if distance >= 20:
                return goodHexes,distance
            for n in tryThese:
                if n not in goodHexes:
                    if searchKind(something,n):
                        goodHexes.append(n)
                    elif something == forest and searchKind(oldForest,n):
                        goodHexes.append(n)
            if len(goodHexes) > 0:
                return goodHexes,distance
            tryThese,blackList = self.searchLoop(something,
                                    tryThese,blackList)
            distance += 1

##################### THESE ARE FOR A* ###############################


    def backTrackPath(self,curHex,start,nodesFromStart):
        path = [curHex]
        while start not in path:
            curHex = path[(len(path) -1)]
            value = nodesFromStart[curHex]
            adjctHexes = findAdjct(curHex[0],curHex[1])
            for nextHex in adjctHexes:
                if nextHex in nodesFromStart and nodesFromStart[nextHex] < value:
                    value = nodesFromStart[nextHex]
                    bestHex = nextHex
            path.append(bestHex)
        tempList = []
        while len(path) > 0:
            tempList.append(path[(len(path) - 1)])
            del path[(len(path) - 1)]
        
        return tempList


    #This decides whether or not to update the priority queue, and then updates accordingly
    def addPriority(self,priorityQ,curHex,value,nodeValues):
        if len(priorityQ) == 0:
            priorityQ.append(curHex)
        else:
            if curHex in priorityQ:
                if nodeValues[curHex] <= value:
                    return priorityQ,nodeValues
                else:
                    for n in range(0,len(priorityQ)):
                        if priorityQ[n] == curHex:
                            del priorityQ[n]
                            break
        addedSomething = False
        for n in range(0,len(priorityQ)):
            if nodeValues[priorityQ[n]] > value:
                tempList = priorityQ[:n] + [curHex] + priorityQ[n:]
                priorityQ = tempList
                addedSomething = True
                break
        if addedSomething == False:
            priorityQ.append(curHex)
        nodeValues[curHex] = value
        return priorityQ,nodeValues

    #updates all my various lists for a specific hex.
    def updateValues(self,nextHex,priorityQ,nodeValues,nodesFromStart,nodesFromEnd,end,curHex):
        #This is where the travel costs for terrain are defined
        if (nextHex in self.myMap) or nextHex == end:
            if nextHex == end:
                travelCost = 1
            elif self.myMap[nextHex] == forest:
                travelCost = 2
            elif self.myMap[nextHex] == thicket:
                travelCost = 3
            else:
                travelCost = 1
            fromEnd = crowDist(nextHex,end)
            fromStart = (nodesFromStart[curHex] + travelCost)
        
            if nextHex not in nodeValues:
                nodesFromEnd[nextHex] = fromEnd
                nodesFromStart[nextHex] = fromStart

            elif nodesFromStart[nextHex] > fromStart:
                nodesFromStart[nextHex] = fromStart
            
            value = (fromEnd + nodesFromStart[nextHex])
            priorityQ,nodeValues = self.addPriority(priorityQ,nextHex,value,nodeValues)
        
        
        return priorityQ,nodeValues,nodesFromStart,nodesFromEnd

    #This finds the optimal path between two points on the map
    def findRoute(self,start,end):
        gotoMountain = False
        traveled = []
        blackList = []
        priorityQ = [start]
        distance = crowDist(start,end)
        nodeValues = {start:distance}
        nodesFromStart = {start:0}
        nodesFromEnd = {start:distance}
        goodPath = False

        while goodPath == False:
            curHex = priorityQ[0]
            traveled.append(curHex)
            adjctHexes = findAdjct(curHex[0],curHex[1])
            for nextHex in adjctHexes:
                if nextHex not in blackList:
                    inBounds = True
                    inBounds = isInBounds(nextHex[0], nextHex[1])
                    if nextHex not in self.myMap or self.myMap[nextHex] == mountain:
                        inBounds = False
                        if nextHex == end:
                            inBounds = True
                    if inBounds == False:
                        blackList.append(nextHex)
                if nextHex not in blackList:
                    priorityQ,nodeValues,nodesFromStart,nodesFromEnd = self.updateValues(
                        nextHex,priorityQ,nodeValues,nodesFromStart,nodesFromEnd,end,curHex)
            blackList.append(priorityQ[0])
            del priorityQ[0]

            if len(priorityQ) == 0:
                path = []
                return path,0
            if priorityQ[0] == end:
                goodPath = True

                path = self.backTrackPath(priorityQ[0],start,nodesFromStart)
                if end not in self.myMap or self.myMap[end] == mountain:
                    del path[(len(path) -1 )]
        if end in nodesFromStart:
            return path, nodesFromStart[end]
        return path, 0


    
    

##########################################################################

    #unblits and reblits a guy from one hex to the next
    def moveMan(self,x2,y2):
#        print self.jobs
        inBounds = isInBounds(x2,y2)
        color = getHexType((x2,y2))
        if not adjctTo((x2,y2),self.location):
            inBounds = False
        (x1,y1) = self.location
        if inBounds == True and color != mountain:
            y3 = (y1 - 1)
            hexType = getHexType((x1,y1))
            if hexType in range (dirt,forest):
                if getNumTrodden(x1,y1) == 7 and hexType != dirt:
                    setNumTrodden(x1,y1,0)
                    setHexType((x1,y1),hexType-1)
                else:
                    trodden = getNumTrodden(x1,y1)
                    setNumTrodden(x1,y1, trodden + 1)
            numPeople = getNumPeople((x1,y1))
            setNumPeople((x1,y1), numPeople - 1)

            if self.location == curGuy.location:
                blitHex(x1,y3)
#            self.blitMan((x2,y2),man)
            numPeople = getNumPeople((x2,y2))
            setNumPeople((x2,y2),numPeople +1)
#            blitHex((x2,y2))
            self.location = (x2,y2)
            self.updateMyMap()
            return (x2,y2)
        else:
            self.location = (x1,y1)
            self.updateMyMap()
            return (x1,y1)

    #blits a guy somewhere
    def blitMan(self,shortx,shorty,color):
        (shortx,shorty) = (shortx,shorty)
        (x,y) = shortToLong(shortx, shorty)
        y-=2
        x+=8
        color_surface = colorSurf[int(color)]
        color_surface.set_colorkey(White)
        screen.blit(color_surface, (x, y))



class manClass(mobile):
    fed = 0
    sleepBar = 0
    task = 0
    woodSource = (0,0)
    buildSite = (0,0)
    exploreCount = 0
    heavy = []
    light = []
    sleepSpot = (0,0)
    
    def __init__(self,L):
        self.fed = 100
        self.sleepBar = 100
        self.location = L
        self.exploreCount = random.randint(10,20)
        self.priorityQueue = ['BuildHouse','Explore']
        hexAttribList[self.location] += 8
#        self.blitMan((self.location), man)
#        self.myMap[self.location] = hexAttribList[self.location]
        self.myMap = {}
        self.updateMyMap()
        
    def updateMyMap(self):
        adjctHexes = []
        adjctHexes = findAdjct(self.location[0],self.location[1])
        for n in adjctHexes:
#            pdb.set_trace()
            self.myMap[n] = hexAttribList[n]
#            if self == curGuy:
#                blitHex(n)
#        if self == curGuy:
#            blitHex(self.location)
        pygame.display.flip()

    #this blits a hex of a certain color to a specified location
    def blitMyMapHex(self,shortx,shorty):
        (shortx,shorty) = (shortx,shorty)
        (x, y) = shortToLong(shortx, shorty)
        color = (self.myMap[(shortx, shorty)]) % 8
        color_surface = colorSurf[int(color)]
        color_surface.set_colorkey(White)
        screen.blit(color_surface, (x, y))
        numHouses = int(((self.myMap[(shortx, shorty)])%512)/64)
        if numHouses > 0:
            blitHouse(shortx,shorty,house)

    def buildingHutQueue(self):
        #print (7)
        self.jobs,clicks = self.findRoute(self.location,self.woodSource)
        #self.jobs would be empty if he’s standing on the wood source
        #if len(self.jobs) > 0:
        #    del self.jobs[(len(self.jobs)-1)]
        #path,clicks = findRoute(self.woodSource,self.buildSite)
        #self.jobs += path

    def findRandSomething(self,Something):
        nextHex = list(self.myMap.keys())
        if len(nextHex) > 0:
            randNum = random.randint(0,(len(nextHex)-1))
        else:
            return (0,0)
#        print len(nextHex),randNum, "lenth nextHex and randnum"
        curHex = nextHex[randNum]

        if getHexType(curHex) == Something:
            return curHex

        else:
            return (0,0)
    
    def findGoodBuildSite(self):
        self.buildSite = self.findRandSomething(meadow)
        if self.buildSite == (0,0):
            return []
        else:
            return [self.buildSite]


    def newBuildSite(self):
        self.task = 18
        self.jobs = []
        while len(self.jobs) < 1:
            goExploring = False
            goodSite = False
            nearFar = random.randint(0,1)

            if goodSite == False:
                if nearFar == 0:
                    self.buildSite = self.findGoodBuildSite()
                else:
                    self.buildSite,distance = self.findNearest(meadow, self.location)
                if len(self.buildSite)>0:
                    self.buildSite = self.buildSite[0]
                    numHouses = getNumHouses(self.buildSite)
                    if numHouses == 0:
                        goodSite = True
                else:
#                    self.exploreCount = random.randint(10,20)
                    self.updatePriorityQueue('Explore')
                    goExploring = True
            if goExploring == False:
                self.woodSource,distance = self.findNearest(forest, self.buildSite)
                if len(self.woodSource) > 0:
                    self.woodSource = self.woodSource[0]
                    if self.woodSource != (0,0) and self.woodSource:
                        self.jobs,clicks = self.findRoute(self.location,self.woodSource)
                        if len(self.jobs) > 0:
                            del self.jobs[(len(self.jobs)-1)]
                        self.jobs += path
                else:
#                    self.exploreCount = random.randint(10,20)
                    self.updatePriorityQueue('Explore')
        return goExploring


    def findNewSource(self):
        source,distance = findNearest(forest, self.buildSite)
        if source[0] in self.myMap:
            self.jobs,clicks = self.findRoute(self.location,source[0])
            self.woodSource = source[0]
        else:
            self.woodSource = (0,0)

    def buildHouse(self):
        noGoodSite = False
        if len(self.jobs) <= 1:
            if self.task <= 0:
                #finds a wood source and a build site
                #and builds a path from self to wood to build site
                noGoodSite = self.newBuildSite()
            elif self.location == self.woodSource:
                self.jobs,clicks = self.findRoute(self.location, self.buildSite)
            elif self.woodSource != (0,0):
                self.jobs,clicks = self.findRoute(self.location, self.woodSource)
            else:
                self.findNewSource()
                if self.woodSource != (0,0):
                    self.jobs,clicks = self.findRoute(self.location, self.woodSource)
                else:
                    self.updatePriorityQueue('Explore')
            

        #This moves him from place to place
        #and updates his task progress
        if len(self.jobs) > 1 and noGoodSite == False:
            if self.location == self.woodSource:
                if getHexType(self.location) != forest:
                    if getHexType(self.location) != oldForest:
                        self.findNewSource()
                        if self.woodSource == (0,0):
                            self.updatePriorityQueue('Explore')
            self.location = self.moveMan(self.jobs[1][0],self.jobs[1][1])
            if self.jobs[0] == self.woodSource:
                self.task -= 1
                if self.task%6 == 0:
                    hexAttribList[self.jobs[0]] -= (hexAttribList[self.jobs[0]])%8
            if self.jobs[1] == self.buildSite and self.task <= 0:
                    numHouses = getNumHouses(self.buildSite)
                    setNumHouses(self.buildSite,(numHouses + 1))
                    self.home = self.jobs[1]

                
            #This decides how long to wait before moving
            if len(self.jobs) >= 2:
                if self.jobs[1] == self.woodSource or self.jobs[1] == self.buildSite:
                    self.queueCount = 4 + self.moveCost[(hexAttribList[self.jobs[1]])%8]
                else:
                    self.queueCount = self.moveCost[(hexAttribList[self.jobs[1]])%8]
            del self.jobs[0]

    def sleep(self):
        if len(self.jobs) > 1:
            if self.queueCount <= 0:
                self.location = self.moveMan(self.jobs[1][0],self.jobs[1][1])
                del self.jobs[0]
                if len(self.jobs) > 1:
                    self.queueCount = self.moveCost[getHexType(self.jobs[1])]
        else:
            if self.location == self.home:
                self.sleepBar += 5
#                print self.sleepBar, "sleep bar higher"
                if self.sleepBar >= 146:
                    print (self.priorityQueue)
                    print (self.priorityQueue[(len(self.priorityQueue)-1)], "will be deleted")
                    del self.priorityQueue[(len(self.priorityQueue)-1)]
                    print (self.priorityQueue, "now it's gone")
#                    pdb.set_trace()
            else:
                self.sleepBar += 3
#                print self.sleepBar, "sleep bar higher"
                if self.sleepBar >= 78:
                    print (self.priorityQueue)
                    print (self.priorityQueue[(len(self.priorityQueue)-1)], "will be deleted")
                    del self.priorityQueue[(len(self.priorityQueue)-1)]
                    print (self.priorityQueue, "now it's gone")
#                    pdb.set_trace()

    def findSleepSpot(self):
        if self.home != (0,0):
            print (self.priorityQueue)
            self.jobs,distance = self.findRoute(self.location,self.home)
            if distance <= 20 and len(self.jobs) > 1:
                self.queueCount = self.moveCost[getHexType(self.jobs[1])]
                self.sleepSpot = self.home
            else:
                self.sleepSpot = self.location
                self.jobs = []

    def searchDark(self,tryThese,blackList):
        tryThese2 = []
        for n in tryThese:
            newSet = findAdjct(n[0],n[1])
            for n in newSet:
                if n not in tryThese and n not in blackList and isInBounds(n[0],n[1]):
                    if getHexType(n) != mountain or n not in self.myMap:
                        tryThese2.append(n)

        return tryThese2,tryThese

    def findPlaceExplore(self):
        distance = 0
        blackList = []
        tryThese = [self.location]
        goodHexes = []
        while len(goodHexes) == 0:
            tryThese,blackList = self.searchDark(tryThese,blackList)
            for n in tryThese:
                if n not in goodHexes:
                    if n not in self.myMap:
                        goodHexes.append(n)
            if len(goodHexes) > 0:
                return goodHexes
            if distance >= 8:
                return tryThese
            distance += 1

        


    def explore(self):
        if len(self.jobs) > 1:
            self.moveMan(self.jobs[1][0],self.jobs[1][1])
            self.exploreCount -= 1
            del self.jobs[0]
            if len(self.jobs) > 1:   
                self.queueCount = self.moveCost[getHexType(self.jobs[1])]
        if len(self.jobs) <= 1:
            placesToGo = self.findPlaceExplore()
            if len(placesToGo) > 1:
                n = random.randint(0,(len(placesToGo)-1))
            else:
                n = 0
#            print len(placesToGo), n, "places to go and n"
#            print "Going from", self.location, "to", placesToGo[n], crowDist(self.location,placesToGo[n])
            self.jobs,distance = self.findRoute(self.location, placesToGo[n])
#            print self.jobs
            
            self.queueCount = self.moveCost[getHexType(self.jobs[1])]
        if self.exploreCount <= 0 and self.priorityQueue[(len(self.priorityQueue)-1)] == 'Explore':
            del self.priorityQueue[(len(self.priorityQueue)-1)]


    def searchLoop(self,something,tryThese,blackList):
        tryThese2 = []
        for n in tryThese:
            newSet = findAdjct(n[0],n[1])
            for n in newSet:
                if n not in tryThese and n not in blackList and isInBounds(n[0],n[1]) and n in self.myMap:
                    if getHexType(n) != mountain or something == mountain:
                        tryThese2.append(n)

        return tryThese2,tryThese


#returns a list of the closest given thing to a set of coordinates
    def findNearest(self, something, curHex):
        distance = 0
        if searchKind(something,curHex):
            return [curHex],distance
        blackList = []
        tryThese = [curHex]
        goodHexes = []
        while len(goodHexes) == 0:
    #        pdb.set_trace()
            if distance >= 20:
                return goodHexes,distance
            for n in tryThese:
                if n not in goodHexes:
                    if searchKind(something,n):
                        goodHexes.append(n)
                    elif something == forest and searchKind(oldForest,n):
                        goodHexes.append(n)
            if len(goodHexes) > 0:
                return goodHexes,distance
            tryThese,blackList = self.searchLoop(something,
                                    tryThese,blackList)
            distance += 1



    def live(self):
        #This timer is populated by terrain and working costs
        self.queueCount-= 1
        self.sleepBar -= 1
#        print self.sleepBar, "sleep bar lower"
#        if self.sleepBar < 21:
#            pdb.set_trace()

        if (self.sleepBar <= 20) and ('Sleep' not in self.priorityQueue):
            self.updatePriorityQueue('Sleep')
            if self.location != self.sleepSpot:
                self.findSleepSpot()

        #This doesn't move him if still working or reducing terrain cost
        if self.queueCount <= 0:
            #priorityQueue should always include all the activities.
            #The last on the list will be executed.
            #activities include sleep,buildHouse,explore
            curActivity = self.priorityQueue[(len(self.priorityQueue)-1)]
            if curActivity == 'Sleep':
                self.sleep()
            elif curActivity == 'Explore':
                self.explore()
            elif curActivity == 'BuildHouse':
                self.buildHouse()
            curActivity = self.priorityQueue[(len(self.priorityQueue)-1)]
            if curActivity != 'Sleep' and self.location != self.sleepSpot and self.sleepSpot != (0,0):
                self.updateMyMap()
                
    

############################# BEGIN SETUP ###################################

createMap()

#blits a guy somewhere
numberOfGuys = int(input("How many guys do you want?"))
for n in range(0,numberOfGuys):
    found = False
    while found == False:
        randHex = findRandomHex()
        if getHexType(randHex) != mountain:
            found = True
    curGuy = input("What will this guy be called?")
    curGuy = manClass(randHex)
    allGuys.append(curGuy)
    setNumPeople(randHex,1)


#theGuy = manClass(randHex)
#anotherGuy = manClass(randHex)
setNumPeople(randHex,1)

pygame.display.flip()

################################   SETUP COMPLETE   ############################

while quitgame == False:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                print ("dirt")
                newColor = dirt
                go = True
            if event.key == pygame.K_2:
                print ("meadow")
                newColor = meadow
                go = True
            if event.key == pygame.K_3:
                print ("thicket")
                newColor = thicket
                go = True
            if event.key == pygame.K_4:
                print ("forest")
                newColor = forest
                go = True
            if event.key == pygame.K_5:
                print ("mountain")
                newColor = mountain
                go = True
            if event.key == pygame.K_6:
                print ("house")
                newColor = house
                go = True
            if event.key == pygame.K_7:
                go = False
            if event.key == pygame.K_8:
                print (hexAttribList)
            if event.key == pygame.K_9:
                for n in hexAttribList:
                    blitHex(n[0],n[1])
                pygame.display.flip()

            if event.key == pygame.K_h:
                if len(jobs) > 0:
                    jobs,self.location = followPath(jobs)
            if event.key == pygame.K_m:
                nearest,distance = findNearest(newColor, self.location)
                if len(nearest) > 0:
                    if distance > 0:
                        end = nearest[0]
                        jobs,clicks = self.findRoute(self.location,end)
                        jobs,self.location = followPath(path)
                    else:
                        print ("I'm standing on one!!")
                else:
                    print ("I can't find one.")

# This event makes things grow and burn by pressing enter, is Mutation Valley
            if event.key == pygame.K_RETURN:
                running = True
                while running == True:
                    timer = pygame.time.get_ticks()

                    grow()
                    for n in allGuys:
                        n.live()

                    theseHexes = findAdjct(curGuy.location[0],curGuy.location[1])
                    for n in theseHexes:
                        blitHex(n[0],n[1])
                    blitHex(curGuy.location[0],curGuy.location[1])
                    pygame.display.flip()
                    gameTime += 1
#                    if gameTime%500 == 0:
#                        pdb.set_trace()
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                running = False
                                print (gameTime)
                            if event.key == pygame.K_TAB:
                                curGuy = allGuys.pop(0)
                                allGuys.append(curGuy)
                                pygame.draw.rect(screen, (0,0,0),(0, 0, winsizex, winsizey))
#                                pygame.display.flip()
#                                pdb.set_trace()
                                for n in curGuy.myMap:
                                    curGuy.blitMyMapHex(n[0],n[1])
                                curGuy.updateMyMap()
                                pygame.display.flip()
                                    

                    time = (pygame.time.get_ticks() - timer)
                    if time > 30000:
                        pdb.set_trace()
                    if time < 45:
                        pygame.time.wait(50 - time)




        if event.type == MOUSEBUTTONDOWN:
            wheremouse = pygame.mouse.get_pos()
            (xblit, yblit) = findHexClicked(wheremouse[0],wheremouse[1], False)
            if go == True:
                if isInBounds(xblit,yblit):
                    hexAttribList[(xblit, yblit)] += (newColor - (hexAttribList[(xblit, yblit)])%8)
                    blitHex(xblit, yblit)
                    pygame.display.flip()



########################

        if event.type == pygame.QUIT:
            quitgame = True
