# -*- coding: utf-8 -*-
#Team Quasingo
#developDataset.py
#script that is used to develop the dataset based on the processed documents
#available to us

#imports

#for the nltk package, see http://www.nltk.org/index.html
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
import nltk
#for standard processing
import unicodecsv
import codecs # for unicode
import os

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

def importCausalVerbDict(csvFilename): #helper for importing the causal verb
    #dictionary
    causalVerbArray = importCSV(csvFilename)
    legend = causalVerbArray[0] #will make reference to this
    causalVerbDict = {}
    #then build upon this
    for i in xrange(1,len(causalVerbArray)):
        givenWordObservation = causalVerbArray[i]
        #find indices
        givenWordDict = {}
        givenWordDict["posScore"] = givenWordObservation[
                                        legend.index("posScore")]
        givenWordDict["negScore"] = givenWordObservation[
                                        legend.index("negScore")]
        givenWordDict["objScore"] = givenWordObservation[
                                        legend.index("objScore")]
        #then add to verb dict
        causalVerbDict[givenWordObservation[0]] = givenWordDict
    #now built, we shall return
    return causalVerbDict

def attachToCausalVerbDict(causalVerb,causalVerbDict): #helper for attaching 
    #a particular causal verb to our dictionary
    givenVerbDictionary = {}
    #extract word of causal verb
    causalVerb = causalVerb.name()
    #add positive, negative, and objective scores to this
    givenVerbDictionary["posScore"] = swn.senti_synset(causalVerb).pos_score()
    givenVerbDictionary["negScore"] = swn.senti_synset(causalVerb).neg_score()
    givenVerbDictionary["objScore"] = swn.senti_synset(causalVerb).obj_score()
    #then attach that dictioanry to the causal verb dict
    causalVerbDict[causalVerb] = givenVerbDictionary

def causalDictToArray(causalVerbDict): #helper that builds our array for
    #export
    givenArray = [["causalVerb","posScore","negScore","objScore"]]
    for verb in causalVerbDict:
        verbLine = [verb] #we will add to this
        for i in xrange(1,len(givenArray[0])): #go through references
            verbLine.append(causalVerbDict[verb][givenArray[0][i]])
        #now attach it to our givenArray
        givenArray.append(verbLine)
    return givenArray

def getCausalVerbs(causalFilename): #helper for building our dataset of
    #causal verbs
    causalVerbDict = {} #we will add to this dict
    for synset in (wn.all_synsets()):
        for causalVerb in synset.causes(): #where we find causal verbs
            attachToCausalVerbDict(causalVerb,causalVerbDict) #process of 
                #attaching to causal verb dict
    #at this point, need to flatten dict into array
    causalVerbArray = causalDictToArray(causalVerbDict)
    #then export it
    exportToCSV(causalVerbArray,causalFilename)

def importAndTokenizeDocument(documentFilename): #helper for importing and
    #tokenizing our desired document
    documentFile = codecs.open(documentFilename,"r","utf-8-sig")
    tokenizedList = [] #we will add to this
    for fileLine in documentFile.read().splitlines(): #we will pull from this
        givenSentenceTokens = nltk.word_tokenize(fileLine) #gives us 
        #sentence tokens
        #then add them to our list
        tokenizedList.extend(givenSentenceTokens)
    return tokenizedList

def adjustVerbName(verb): #helper for adjusting a given verb name from
    #synset to normal structure
    return verb.split(".")[0]

def buildObsDict(obsVerb,prevWord,sucWord,synsetObsVerb,causalVerbDict):
    #main function for building our dictionary for a observation
    obsDict = {}
    #add our words
    obsDict["obsVerb"] = obsVerb
    obsDict["prevWord"] = prevWord
    obsDict["sucWord"] = sucWord
    obsDict["synsetObsVerb"] = synsetObsVerb
    #then add direction
    obsDict["posScore"] = causalVerbDict[synsetObsVerb]["posScore"]
    obsDict["negScore"] = causalVerbDict[synsetObsVerb]["negScore"]
    obsDict["objScore"] = causalVerbDict[synsetObsVerb]["objScore"]
    #then return
    return obsDict

def findCausalLinksInDocument(documentFilename,causalVerbDict): #helper for
    #finding causal links within a given document
    tokenizedDoc = importAndTokenizeDocument(documentFilename)
    causalLinkList = [] #we will add to this
    for wordInd in xrange(len(tokenizedDoc)):
        word = tokenizedDoc[wordInd]
        for verb in causalVerbDict:
            adjVerb = adjustVerbName(verb) #quick helper to account for synset
                                #structure of the initial verb name
            #look through tokenized doc for this word
            if (adjVerb == word.lower() or
                    (adjVerb in word.lower() and
                    len(word)-len(adjVerb) <= 2)): #we have some indication 
                    #of causality, so get previous word and succeeding word
                if (wordInd > 0):
                    prevWord = tokenizedDoc[wordInd-1]
                else:
                    prevWord = "<start>"
                #get next work
                if (wordInd < len(tokenizedDoc)-1):
                    sucWord = tokenizedDoc[wordInd+1]
                else:
                    sucWord = "<end>"
                #append observation to the list
                obsDict = buildObsDict(word,prevWord,sucWord,verb,
                                        causalVerbDict)
                causalLinkList.append(obsDict)
                #then stop the loop
                break
    return causalLinkList

def exportDocumentCausalDict(docName,givenDocCausalList,outputFilename): 
    #helper for exporting each causal dict back to our output file
    outputArray = importCSV(outputFilename)
    legend = outputArray[0] #for keeping track of indices
    for causalLink in givenDocCausalList:
        causalLinkList = [None for i in legend] #will add to this
        #make mapping
        for legendFieldInd in xrange(len(legend)):
            legendField = legend[legendFieldInd]
            if (legendField == "docName"): #not in dictionary
                causalLinkList[legendFieldInd] = docName
            else: #pull from dictionary
                causalLinkList[legendFieldInd] = causalLink[legendField]
        #now that we made that mapping, append to output array
        outputArray.append(causalLinkList)
    #now export
    exportToCSV(outputArray,outputFilename)

def startOutputFile(outputFilename): #main method for starting to build the
    #final dataset
    outputArray = [["docName","obsVerb","synsetObsVerb","prevWord","sucWord",
                    "posScore","negScore","objScore"]]
    exportToCSV(outputArray,outputFilename)

def buildDocumentCausalDictionary(processedDirName,causalVerbDict,
                                    outputFilename):
    #main function for building a document causal dictionary
    documentCausalDict = {} #will add documents to this
    for filename in os.listdir(processedDirName):
        if (filename != "consideredDocuments.txt" and
                filename != "causalVerbs.csv"): #these are special documents,
            #do not touch them
            fullDocumentFilename = processedDirName + os.sep + filename
            #get causal links
            givenDocCausalList = findCausalLinksInDocument(
                                    fullDocumentFilename,causalVerbDict)
            documentCausalDict[filename] = givenDocCausalList
            #when done, export for safety sake
            print filename #for debugging purposes
            exportDocumentCausalDict(filename,givenDocCausalList,outputFilename)

#main functions

def developDataset(processedDirName,outputFilename,causalVerbDictFilename=None):
    #amin function of the process
    if (causalVerbDictFilename == None): #need to generate this
        causalVerbDictFilename = "../processedDocuments/causalVerbs.csv"
        getCausalVerbs(causalVerbDictFilename) #generates the file
    #now perform the process
    startOutputFile(outputFilename)
    causalVerbDict = importCausalVerbDict(causalVerbDictFilename)
    buildDocumentCausalDictionary(processedDirName,causalVerbDict,
                                        outputFilename)

#process
developDataset("../processedDocuments","../outputFile.csv",
                                "../processedDocuments/causalVerbs.csv")
