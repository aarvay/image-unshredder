'''Instagram Engineering Challenge. 
	
	Problem : http://instagram-engineering.tumblr.com/post/12651721845/
	Author : Vignesh Rajagopalan <vignesh@campuspry.com>
	File : unshred.py
	Desc : Takes a shredded image as input and unshreds it.
	
'''
from PIL import Image
from math import sqrt
import sys

if (len(sys.argv) <> 3):
	print "Usage : python unshred.py /path/to/input/image /path/to/output/image"
	sys.exit()

def getPixelValue(x, y):
	pixelData = shreddedImage.getdata()
	pixel = pixelData[y * width + x]
	return pixel

def computeStripDifference(colourRange, height, score):
	return int(round(height / colourRange) - score)

def computeDistance(p, q):
	r = p[0] - q[0]
	g = p[1] - q[1]
	b = p[2] - q[2]
	distance = sqrt(( r*r + g*g + b*b ))
	return distance

def computeScore(strip1, strip2, stripWidth, colourRangeSize):
	score = 0
	threshold = 30 #Based on some heuristics

	for i in range(0, height, colourRangeSize):
		avgPixel1 = [0, 0, 0, 0]
		avgPixel2 = [0, 0, 0, 0]
		for colourRange in range(0, colourRangeSize):
			if i+colourRange < height:
				pixel1 = getPixelValue((stripWidth*strip1)+(stripWidth-1), (i+colourRange))
				pixel2 = getPixelValue((stripWidth*strip2), (i+colourRange))
				for j in range(0, 3):
					avgPixel1[j] = avgPixel1[j] + pixel1[j]
					avgPixel2[j] = avgPixel2[j] + pixel2[j]
		for j in range(0, 3):
			avgPixel1[j] = avgPixel1[j] / colourRangeSize
			avgPixel2[j] = avgPixel2[j] / colourRangeSize
				
		distance = computeDistance(avgPixel1, avgPixel2)
		if distance < threshold:
			score = score + 1
	return score
	
def findBestNeighbour(strip, colourRange):
	bestScore = -1
	bestNeighbour = -1
	
	for currentStrip in range(0, totalStrips):
		if currentStrip <> strip:
			currentScore = computeScore(strip, currentStrip, stripWidth, colourRange)
			if currentScore > bestScore:
				bestScore = currentScore
				bestStrip = currentStrip
	
	return (bestStrip, bestScore)

def unshred(shreddedImage):
	score = 1<<29
	finalStrip = -1
	stripMap = {}
	colourRange = 8 #Upto 8 works good! stepping in eights saves some time
	
	for strip in range(0, totalStrips):
		neighbour = findBestNeighbour(strip, colourRange)
		stripMap[neighbour[0]] = strip
		if neighbour[1] < score:
			score = neighbour[1]
			finalStrip = strip
	
	nextStrip = finalStrip
	unshreddedImage = Image.new("RGBA", shreddedImage.size)
	
	for strip in range(totalStrips-1, -1, -1):
		x1, y1 = (stripWidth * nextStrip), 0
		x2, y2 = (x1 + stripWidth), height
		source = shreddedImage.crop((x1, y1, x2, y2))
		destination = (strip*stripWidth), 0
		unshreddedImage.paste(source, destination)
		if nextStrip in stripMap.keys():
			nextStrip = stripMap[nextStrip]
	
	unshreddedImage.save(sys.argv[2])

def computeStripWidth():
	minStripWidth = 2
	maxStripWidth = width / 2
	stripWidth = - 1<<29 #Random negative value
	stripDifference = -1
	threshold = 2 #This value worked out to be the best!
	
	for currentStripWidth in range(minStripWidth, maxStripWidth+1, 1):
		if width % currentStripWidth <> 0:
			continue
		
		total=0
		for i in range(0, (width / currentStripWidth)):
			if (i+1) < (width / currentStripWidth):
				result = computeStripDifference(8, height, computeScore(i, i+1, currentStripWidth, 8))
				total += result
				
			avgStripDifference = total / (width / currentStripWidth)
		if avgStripDifference > stripDifference:
			if currentStripWidth % stripWidth == 0:
				if abs(avgStripDifference - stripDifference) <= threshold:
					continue
			stripWidth = currentStripWidth
			stripDifference = avgStripDifference
	return stripWidth

try:
	shreddedImage = Image.open(sys.argv[1])
	width, height = shreddedImage.size
	stripWidth = computeStripWidth()
	totalStrips = width / stripWidth
	unshred(shreddedImage)
except(IOError):
	print "Invalid input."
