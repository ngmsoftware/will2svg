#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 11:09:11 2018

@author: ninguem
"""
from matplotlib import pyplot as plt
from zipfile import ZipFile
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.decoder import wire_format
from google.protobuf.internal.decoder import struct
import os
import sys
import fnmatch
from cairosvg import svg2svg
from subprocess import run

# sudo apt-get install   python3-matplotlib    python3-tk   cairosvg



VERBOSE = False

# General purpose functions
#


def debugPrint(str=''):
    """ debugPrint
It is simply a wrapper to print that you can turn on or off in order to debug
the outputs of the program    
    """
    
    if VERBOSE:
        print(str)
    

def cumsum(dv, factor):
    """ cumsum(dv, factor)
Function that returns the cummulative sum of an array

dv     : array to be cumsummed
factor : factor to be used to divide the array (just to facilitate the specific
         usage in this program)    
    """
    
    res = [0]
    for v in dv:
        res.append(v+res[-1])
    
    return [v/factor for v in res[1:]]


def plotXYLineData(xData, yData, lineData):
    """ plotXYLineData(xData, yData, lineData)
Plots the object in the array of arrays xData, yData and lineData 

xData    : array with arrays of x coordinates
yData    : array with arrays of y coordinates
lineData : array with arrays of lineWhidths
    """

    for x, y, lineWidth in zip(xData, yData, lineData):
        plt.plot(x,[-y for y in y],'k', linewidth=(lineWidth**5)/20)
    
    plt.axis('equal')


def XYLineDataToSVG(xData, yData, lineData):
    """ XYLineDataToSVG(xData, yData, lineData)
Generates the SVG spline data for the array of arrays xData, yData and lineData 
Currently it ignores the linewidth so it generates constant width paths

xData    : array with arrays of x coordinates
yData    : array with arrays of y coordinates
lineData : array with arrays of lineWhidths
skips    : number of spline control points to skip

TODO: Take linewidhts into consideration    
    """

    svgStr = f''
    
    minX = 10000
    minY = 10000
    maxX = -10000
    maxY = -10000
    
    for arrayX, arrayY in zip(xData, yData):
        svgStr += f'<path stroke="black" fill="none" d="M{arrayX[0]},{arrayY[0]} '
        idxr = range(len(arrayX))
        svgStr += f' L'
        for x, y, idx in zip(arrayX[1:], arrayY[1:], idxr[1:]):
            
            svgStr += f'{x} {y},'
    
            minX = x if minX>x else minX
            minY = y if minY>y else minY
            maxX = x if maxX<x else maxX
            maxY = y if maxY<y else maxY
    
        svgStr = svgStr[:-1] + '"/>\n'
    
    svgWidth = maxX-minX
    svgHeight = maxY-minY
    svgStr = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{svgWidth}mm" height="{svgHeight}mm" viewBox="{minX} {minY} {maxX} {maxY}"> ' + svgStr + '</svg>'
        
    return svgStr



# Protobuffer specific functions
#


def unzigzag(v):
    """ unzigzag(v)
Function to convert an unsigned integer into a signed integer via zigzap
method. This is a format used in most protobuffer situations

v : array to unzigzag
    """
    r = -(v+1)/2 if not v%2 == 0 else v/2
    
    return int(r)




def decodeVarintArray(strBytes):
    """ decodeVarintArray(strBytes)
Decodes the array of bytes in the format Varint to signed integers.
Most protobuffer data comes in packages of varint type. This function "unpacks"
the array and returns an array of signed integers.

strBytes : array to unpack
    """

    values = []
    
    nextPos = 0
    while nextPos < len(strBytes):
        value, nextPos = _DecodeVarint32(strBytes, nextPos)
        values.append(value)
        
    return [unzigzag(v) for v in values]
        





# WILL format specific functions
#
    

def decodeMessagePacket(messageBytes):
    """ decodeMessagePacket(messageBytes):
    Decodes the message package in the WILL format and returns the vector of
    location ponts x, y and the linewidths.
    It assumes that the message is in the format specified in the WILL file format
    form Wacom. 
    Future versions might break this code, since its based on the format from 2018.


    messageBytes : message to decode
    """

    nextPos = 0
    
    # startParameter  [FLOAT]
    #  (varint header)
    msgVarintIdentifier, nextPos = _DecodeVarint32(messageBytes, nextPos)
    field, wireType = wire_format.UnpackTag(msgVarintIdentifier)
    #  value
    startParameter =struct.unpack('f',messageBytes[nextPos:nextPos+4])[0]
    nextPos += 4

    debugPrint(f'field: {field}, wire type:{wireType}')
    debugPrint(f'startParameter: {startParameter}')


    # stopParameter  [FLOAT]
    #  (varint header)
    msgVarintIdentifier, nextPos = _DecodeVarint32(messageBytes, nextPos)
    field, wireType = wire_format.UnpackTag(msgVarintIdentifier)
    #  value
    stopParameter = struct.unpack('f',messageBytes[nextPos:nextPos+4])[0]
    nextPos += 4

    debugPrint(f'field: {field}, wire type:{wireType}')
    debugPrint(f'stopParameter: {stopParameter}')

    
    # decimalPrecision  [VARIANT]
    #  (varint header)
    msgVarintIdentifier, nextPos = _DecodeVarint32(messageBytes, nextPos)
    field, wireType = wire_format.UnpackTag(msgVarintIdentifier)
    #  value
    decimalPrecision, nextPos = _DecodeVarint32(messageBytes, nextPos)

    debugPrint(f'field: {field}, wire type:{wireType}')
    debugPrint(f'decimalPrecision: {decimalPrecision}')
    

    # x,y sequence  [BYTE STRING]
    #  (varint header)
    msgVarintIdentifier, nextPos = _DecodeVarint32(messageBytes, nextPos)
    field, wireType = wire_format.UnpackTag(msgVarintIdentifier)
    #  value
    strLen, nextPos = _DecodeVarint32(messageBytes, nextPos)
    xyBytes = messageBytes[nextPos:nextPos+strLen]
    nextPos += strLen
    xyList = decodeVarintArray(xyBytes)
    
    dx = xyList[0::2]
    dy = xyList[1::2]
    
    factor = 10**decimalPrecision
    
    x = cumsum(dx, factor)
    y = cumsum(dy, factor)
    
    debugPrint(f'field: {field}, wire type:{wireType}')
    debugPrint(f'strLen: {strLen}')
    debugPrint(f'x [{len(x)}]: {x[0:10]}...')
    debugPrint(f'y [{len(y)}]: {y[0:10]}...')




    # stroke width  [BYTE STRING]
    #  (varint header)
    msgVarintIdentifier, nextPos = _DecodeVarint32(messageBytes, nextPos)
    field, wireType = wire_format.UnpackTag(msgVarintIdentifier)
    #  value
    strLen, nextPos = _DecodeVarint32(messageBytes, nextPos)
    strokeWidthBytes = messageBytes[nextPos:nextPos+strLen]
    nextPos += strLen
    strokeWidthList = decodeVarintArray(strokeWidthBytes)
    
    strokeWidths = cumsum(strokeWidthList, 1.0)
    
    debugPrint(f'field: {field}, wire type:{wireType}')
    debugPrint(f'strLen: {strLen}')
    debugPrint(f'strokeWidthList [{len(strokeWidths)}]: {strokeWidths[0:10]}...')
    

    # color values  [BYTE STRING]
    #  (varint header)
    msgVarintIdentifier, nextPos = _DecodeVarint32(messageBytes, nextPos)
    field, wireType = wire_format.UnpackTag(msgVarintIdentifier)
    #  value
    strLen, nextPos = _DecodeVarint32(messageBytes, nextPos)
    colorValuesBytes = messageBytes[nextPos:nextPos+strLen]
    nextPos += strLen
    colorValueList = decodeVarintArray(colorValuesBytes)
    
    debugPrint(f'field: {field}, wire type:{wireType}')
    debugPrint(f'strLen: {strLen}')
    debugPrint(f'colorValueList [{len(colorValueList)}]: {colorValueList}')

    debugPrint()
    
    debugPrint(struct.unpack('B'*len(messageBytes[nextPos:]),messageBytes[nextPos:]))

    lineWidth = 0.01*sum(strokeWidths)/len(strokeWidths)
    
    #plt.plot(x,y,'k', linewidth=(lineWidth**5)/20)

    #plt.axis('equal')
    
    return (x, y, lineWidth)


def processBuffer(buffer):
    """ processBuffer(buffer)
Process each message packet in WILL format and return an array of arrays of
x,y, lineWidth values.
The buffer should be the paths.protobuf file in the WILL mini filesystem.
This function walks through each message packet and decodifies it, assembling
the array of vectors x, y and linewidth

buffer : Whole protobuffer read from the WILL file.
    """

    xData = []
    yData = []
    lineData = []
    minX = 10000
    maxX = -10000
    minY = 10000
    maxY = -10000
    
    buffPos = 0
    while buffPos < len(buffer):
        messageLength, buffPos = _DecodeVarint32(buffer, buffPos)
        messageBytes = buffer[buffPos:buffPos+messageLength]
        buffPos += messageLength
        
        #print(f'messageLength = {messageLength}')
        #print('messageBytes:')
        #print(messageBytes)
        
        (x, y, lineWidth) = decodeMessagePacket(messageBytes)
        
        xData.append(x)
        yData.append(y)
        lineData.append(lineWidth)

        
    return (xData, yData, lineData)

        
   


def readWillProtobuff(inputFile):
    """ readWillProtobuff(inputFile)
Reads the content of the paths.protobuf in the will filesystem at the file
inputfile. 
It uncompresses the will file (yes, its a simple zip file) and reads the
content of the file at sections/media/paths.protobuf. It them returns the whole
bytes buffer 

inputFile : string with the .will file.
    """
    
    input_zip=ZipFile(inputFile)
    zip_namelist=input_zip.namelist()
    strokes_protobuf=fnmatch.filter(zip_namelist,'sections/media/*.protobuf')
    debugPrint(strokes_protobuf[0])

    # return input_zip.read(strokes_protobuf[0])
    return map(input_zip.read, strokes_protobuf)




if __name__=='__main__':

    if not len(sys.argv) == 2:
        print('Usage: will_reader.py [filename]\n where filename is the name of the WILL file without the extension.\n\n Obs.: the file.svg will be overitten')
    else:
        fileName = sys.argv[1]

        buffer=readWillProtobuff(fileName + '.will')
        for i,n in zip(buffer,range(99)):
            print(n)
            (xData, yData, lineData) = processBuffer(i)

            plotXYLineData(xData, yData, lineData)

            svgStr = XYLineDataToSVG(xData, yData, lineData)

            datei_name=fileName +'_'+str(n).zfill(2)+ '.svg'

            svg2svg(bytestring=svgStr, write_to=datei_name)
            run(['svgtoipe',datei_name],shell=False)


            # with open(fileName +'_'+str(n).zfill(2)+ '.svg','wt') as f:
            #     f.write(svgStr)



#        buffer = readWillProtobuff(fileName + '.will')
#    
#    
#        (xData, yData, lineData) = processBuffer(buffer)
#    
#    
#        plotXYLineData(xData, yData, lineData)
#        
#        svgStr = XYLineDataToSVG(xData, yData, lineData)
#        
#
#        with open(fileName + '.svg','wt') as f:
#            f.write(svgStr)
#        
    
    