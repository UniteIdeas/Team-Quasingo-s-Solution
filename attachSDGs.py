# -*- coding: utf-8 -*-
#Team Quasingo
#attachSDGs.py
#script designed to take our output dataset and attach the desired sdgs to said
#dataset 
#imports
#for the nltk package, see http://www.nltk.org/index.html
import nltk
#for unicodecsv package, see https://pypi.python.org/pypi/unicodecsv
import unicodecsv
#standard imports
import os
import codecs

#helpers

def exportToCSV(givenArray,csvFilename): #helper for exporting sheet to .csv
    #file
    csvFile = open(csvFilename,"wb")
    givenCSV = unicodecsv.writer(csvFile)
    for row in givenArray:
        givenCSV.writerow(row)

def importCSV(csvFilename): #helper for importing a .csv file, returns imported
    #array
    csvFile = open(csvFilename,"rb")
    givenCSV = unicodecsv.reader(csvFile)
    givenArray = [] #we will append to this
    for line in givenCSV:
        givenArray.append(line)
    #now return it
    return givenArray

def createWordDictionary(sdgFilename): #helper for generating the dictionary
    #over the words found in the .txt file
    sdgFile = codecs.open(sdgFilename,"r","utf-8-sig")
    sdgWordDict = {} #we will add to this
    wordCount = 0 #used for normalizing the proportions
    for fileLine in sdgFile.read().splitlines(): #we will pull from these
        givenSentenceTokens = nltk.word_tokenize(fileLine)
        for token in givenSentenceTokens:
            #add to sdg word dict
            wordCount += 1 #for normalizing purposes
            if (token.lower() in sdgWordDict): #add to proportion
                sdgWordDict[token.lower()] += 1
            else: #make new section
                sdgWordDict[token.lower()] = 1
    #now normalize the dictionary
    for token in sdgWordDict:
        sdgWordDict[token] = float(sdgWordDict[token]) / wordCount
    return sdgWordDict

def generateSDGDict(sdgDirFilename): #helper for generating the dictionary
    #that hold
    sdgDict = {}
    for sdgFilename in os.listdir(sdgDirFilename):
        #make word dictionary
        givenSDGWordDict = createWordDictionary(
                sdgDirFilename + os.sep + sdgFilename)
        #make it smaller for reference
        sdgFilename = sdgFilename[:len(sdgFilename)-len(".txt")]
        sdgDict[sdgFilename] = givenSDGWordDict
    return sdgDict

def alterOutputArray(array): #helper that changes the legend of the output
    #array
    array[0]= ["docName","obsVerb","synsetObsVerb","prevWord","sucWord",
                    "posScore","negScore","objScore","sdgPrevWord","sdgSucWord"]
    #designed to ensure same space
    for i in xrange(1,len(array)): #extend by two
        array[i] = array[i][:len(array[0])] #caps length
        if (len(array[i]) < len(array[0])): #add more
            array[i].extend([None for i in xrange(len(array[0])-len(array[i]))])

def satisfiesPrevWord(word,prevWord): #general logic constraints to see if the 
    #word satisfies near qualities of being prev word
    try:
        return ((word == prevWord.lower()) or
            (word in prevWord.lower() and len(prevWord) - len(word) <= 2)#close
            or
            (prevWord.lower() in word and len(word) - len(prevWord) <= 2))#close
    except:
        print word
        return False

def satisfiesSucWord(word,sucWord): #general logic constraints to see if the 
    #word satisfies near qualities of being suc word
    try:
        return ((word == sucWord.lower()) or
            (word in sucWord.lower() and len(sucWord) - len(word) <= 2)#close
            or
            (sucWord.lower() in word and len(word) - len(sucWord) <= 2))#close
    except:
        print word
        return False


def findSDGEleven(outputArray,sdgDict,outputFilename): #helper that looks for 
    #sdg 11 words in output array
    legend = outputArray[0] #for referencing words
    for row in xrange(1,len(outputArray)):
        for word in sdgDict["sdg11"]: #because using sdg dict 11
            if (satisfiesPrevWord(word,
                outputArray[row][legend.index("prevWord")])): #indicate sdg 11
                outputArray[row][legend.index("sdgPrevWord")] = "sdg11"
                break #don't look at any more words
            elif (satisfiesSucWord(word,
                outputArray[row][legend.index("sucWord")])): #indicate sdg 11
                outputArray[row][legend.index("sdgSucWord")] = "sdg11"
                break #don't look at any more words
    #for safety, let's output this to our array
    exportToCSV(outputArray,outputFilename)

def findTopProbSDGs(consideredSDGs,sdgLength): #helper for finding the top 
    #probability of
    topSDGList = [] #will add to this
    for i in xrange(sdgLength): #run through this for appending
        if (consideredSDGs == {}): break #don't consider anymore
        else:
            topProbSDG = max(consideredSDGs, key=lambda j: consideredSDGs[j])
            topSDGList.append(topProbSDG)
            consideredSDGs.pop(topProbSDG) #so we don't consider it in the next
                                        #iteration
    topSDGString = ";".join(topSDGList)
    return topSDGString

def findProperSDGs(outputArray,sdgDict,consideredIndex,consideredWord,
        consideredRow): #helper
    #for finding the necessary sdgs related to the word
    consideredSDGs = {} #will add to this
    for givenSDG in sdgDict:
        for othWord in sdgDict[givenSDG]:
            if (satisfiesSucWord(othWord,consideredWord)): #means the sdg should
                #be considered
                consideredSDGs[givenSDG] = sdgDict[givenSDG][othWord] #gets
                #us the probability that it is this sdg
                break
    #now simplify the amount
    sdgLength = 3 #want only 3 sdgs to consider for other side
    optimalSDGString = findTopProbSDGs(consideredSDGs,sdgLength)
    outputArray[consideredRow][consideredIndex] = optimalSDGString

def findOtherSDGs(outputArray,sdgDict,outputFilename): #attach other SDGs to the
    #listing
    legend = outputArray[0]
    for row in xrange(1,len(outputArray)):
        if (outputArray[row][legend.index("sdgSucWord")] == "sdg11"):
            #then consider looking at previous word
            consideredIndex = legend.index("sdgPrevWord")
            consideredWord = outputArray[row][legend.index("prevWord")]
            findProperSDGs(outputArray,sdgDict,consideredIndex,consideredWord,
                    row)
        elif (outputArray[row][legend.index("sdgPrevWord")] == "sdg11"):
            #then consider succeeding word
            consideredIndex = legend.index("sdgSucWord")
            consideredWord = outputArray[row][legend.index("sucWord")]
            findProperSDGs(outputArray,sdgDict,consideredIndex,consideredWord,
                    row)
#main function

def attachSDGsToLinks(outputFilename,sdgDirFilename): #main function that
    #attaches sdgs to the specified links found
    #import and alter the output array
    outputArray = importCSV(outputFilename)
    alterOutputArray(outputArray)
    #make sdg dict
    sdgDict = generateSDGDict(sdgDirFilename)
    #find sdg eleven
    findSDGEleven(outputArray,sdgDict,outputFilename)
    #find other SDGs
    findOtherSDGs(outputArray,sdgDict,outputFilename)
    #then export
    exportToCSV(outputArray,outputFilename)

#main execution
attachSDGsToLinks("../outputDataset/outputFile.csv",
                        "../processedDocuments/sdgDescriptions")
