#Team Quasingo
#ocrProcess.py
#main script written to processing the documents via ocr

#imports

import os

#helpers

def makeConsideredDocFile(rawDocDirName,processedDocDirName): #helper that 
    #generates the considered doc file for us
    consideredDocFilename = (processedDocDirName + os.sep +
                            "consideredDocuments.txt")
    #get listing generated
    os.system("ls " + rawDocDirName + " > " + consideredDocFilename)
    return consideredDocFilename

def makeConsideredDocList(consideredDocFilename,
    rawDocDirName): #helper that generates the
    #list based on the file
    consideredDocFile = open(consideredDocFilename,"rb")
    consideredDocList = consideredDocFile.read().split("\n") #gets rid of
    #new lines
    filteredConsideredDocList = []
    #now filter them
    for consideredDocName in consideredDocList:
        if (len(consideredDocName) != 0 #indicator of split discrepancy
            and consideredDocName[0] != "#"): #indicator of completion
            filteredConsideredDocList.append(consideredDocName)
    return filteredConsideredDocList

def writeToConsideredDocFile(consideredDocList,consideredDocFilename): #helper
    #that writes our consideredDocList to the considered doc file
    consideredDocFile = open(consideredDocFilename,"wb")
    docString = "\n".join(consideredDocList) #so we can add separating lines
    #to the document
    consideredDocFile.write(docString)
    consideredDocFile.close()


def preProcessDoc(consideredDocName,rawDirName,preProcDirName): #helper for
    #preprocessing a given document name
    preProcDocName = (consideredDocName[:len(consideredDocName) - len("pdf")] +
                        "png") #need a png format
    pixelDensity = 400 #important for conversion method
    #get conversion names from raw to pre-processing
    rawDocFilename = "'" + rawDirName + os.sep + consideredDocName + "'"
    preProcDocFilename = "'" + preProcDirName + os.sep + preProcDocName + "'"
    #then convert
    os.system("convert -density " + str(pixelDensity) + " " + rawDocFilename + 
                    " " + preProcDocFilename)

def performConcatenation(consideredDocName,procDirName): #after processing all
    #the documents into .txt files, perform the concatenation
    #get rid of pdf tag
    tempDocName = consideredDocName[:len(consideredDocName)-len(".pdf")]
    finalConversionName = ("'" + procDirName + os.sep + tempDocName + 
                                ".txt'")
    #get a string of the files we are trying to concatenate and convert
    concatenateString = "'" + procDirName + os.sep + tempDocName + "-'*"
    #then perform concatenation and removal
    os.system("cat " + concatenateString + " > " + finalConversionName)
    os.system("rm " + concatenateString)

def developConvertName(pageName,numPages): #helper for 
    #generating conversion name for correct ordering
    numIndices = len(str(numPages)) #gets number of decimal bits needed
    pageConvertName = pageName[:len(pageName)-len(".png")]
    #indicate length without . handle, with dash, and with number of indices
    pageConvertName = pageConvertName.split("-") #useful for extracting end
    #part
    while (len(pageConvertName[len(pageConvertName)-1]) < numIndices): 
        #need to add indices to this
        pageConvertName[len(pageConvertName)-1] = (
                "0" + pageConvertName[len(pageConvertName)-1])
    #then rejoin
    pageConvertName = "-".join(pageConvertName)
    return pageConvertName

def finalProcessDoc(consideredDocName,preProcDirName,procDirName): #finally
    #turn each .png file into a .txt file, then concatenate those .txt files
    preProcDirLength = len(os.listdir(preProcDirName)) #helper for getting
    #a sense of how big it is
    for pageName in os.listdir(preProcDirName):
        #convert this page via tesseract
        pageConvertName = developConvertName(pageName,preProcDirLength)
        #convert to account for change in directory
        pageConvertName = "'" + procDirName + os.sep + pageConvertName + "'"
        #also alter page png name
        pagePNGName = "'" + preProcDirName + os.sep + pageName + "'"
        os.system("tesseract " + pagePNGName + " " +  pageConvertName)
        os.system("rm " + pagePNGName)
    #now concatenate all of them
    performConcatenation(consideredDocName,procDirName)

#main functions

def convertDocuments(consideredDocList,rawDirName,preProcDirName,procDirName,
                    consideredDocFilename): #main process for OCRing the
    #documents listed in the consideredDocList
    for i in xrange(len(consideredDocList)): #need index for alterations
        consideredDocName = consideredDocList[i]
        #note that it is in the directory of raw documents
        #pre process into a .png
        preProcessDoc(consideredDocName,rawDirName,preProcDirName)
        #then process into .txt files
        finalProcessDoc(consideredDocName,preProcDirName,procDirName)
        #then alter our considered doc file in order to account for completion
        consideredDocList[i] = "#" + consideredDocName # "#" accounts for
                                                    #completion in the script
        writeToConsideredDocFile(consideredDocList,consideredDocFilename)

def processDocuments(rawDocDirName,preProcessedDocDirName,processedDocDirName,
                    consideredDocFilename=None): #main function for
    #processing our given documents
    if (consideredDocFilename == None): #need to generate it
        consideredDocFilename = makeConsideredDocFile(rawDocDirName,
                                                        processedDocDirName)
    #get list of considered documents
    consideredDocList = makeConsideredDocList(consideredDocFilename,
                                                        rawDocDirName)
    
    convertDocuments(consideredDocList,rawDocDirName,preProcessedDocDirName,
                    processedDocDirName,consideredDocFilename)

processDocuments("../rawDocuments","../preProcessedDocuments",
        "../processedDocuments","../processedDocuments/consideredDocuments.txt")
