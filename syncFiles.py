from optparse import OptionParser
from lxml import html
import requests
import json
import os
import re
import time

class syncFiles:
   
    def __init__(self, seriesName, seriesSeason):
        self.seriesName = seriesName
        self.seriesSeason = seriesSeason
        self.seriesEpisodeNames = dict()
        self.mediaExtension = ""
        self.subtitleExtension = ".srt"
        self.subtitleExists = False
        self.fileLocation = ""
        print "Initialized!"

    def downloadEpisodeName(self, wikipage):
        episodeNameData = ""
        page = requests.get(wikipage)
        tree = html.fromstring(page.content)
        table = tree.xpath("//table[@class='wikitable sortable']//*")

        episodeNumber = []
        episodeName = []
        count = 0
        for element in table:
            if element.tag != 'td':
                continue
            if count % 9 == 0:
                episodeNumber.append(element.text_content())
            if count % 9 == 1:
                epi_name = element.text_content()
                epi_name = epi_name.replace('"', '')
                episodeName.append(epi_name)
            count = count + 1

        print episodeNumber
        for index in range(len(episodeNumber)):
            episodeNameData = episodeNameData + episodeNumber[index] + " "
            episodeNameData = episodeNameData + episodeName[index] + "\n"
        #print episodeNameData
        fileName = self.seriesName + ".SEASON." + self.seriesSeason + ".EPISODE.NAMES.txt"
        fileHandle = open(fileName, 'w')
        fileHandle.write(episodeNameData)
        fileHandle.close()
        self.seriesNameFile = fileName

    def readEpisodeName(self):
        actualFileNames = []
        f = open(self.seriesNameFile, "r")
        for line in f:
                actualFileNames.append(line)
        f.close()
        return actualFileNames

    def constrctFileName(self):
        actualNames = self.readEpisodeName()

        for name in actualNames:
            fields = name.split(" ", 1)
            if len(fields) < 2:
                continue
            episodeValues = list()
            episodeNumber = fields[0]
            episodeNumberString = "S" + str(self.getNumberString(int(self.seriesSeason)))
            episodeNumberString = episodeNumberString + "E" + str(self.getNumberString(int(episodeNumber)))
            #print episodeNumberString
            newSuggestedName = self.getSuggestedName(self.seriesName)
            newSuggestedName = newSuggestedName + "-" + episodeNumberString + "-" + self.getSuggestedName(fields[1])
            episodeValues.append(episodeNumber)
            episodeValues.append(episodeNumberString)
            episodeValues.append(newSuggestedName)
            episodeValues.append(self.possibleSearchSuggestions(episodeNumber))
            episodeValues.append(fields[1])
            episodeValues.append("")
            episodeValues.append("")
            self.seriesEpisodeNames[fields[0]] = episodeValues

        print(json.dumps(self.seriesEpisodeNames, indent = 2))

    def getNumberString(self, value):
        if(value < 10):
            return "0" + str(value)
        else:
            return value

    def getSuggestedName(self, name):
        newName = name.replace("\n", "").replace("\r", "").replace(" ", ".")
        return newName

    def possibleSearchSuggestions(self, episode):
        possibles = list()
        #possibles.append(str(episode))
        name = "S" + str(self.getNumberString(int(self.seriesSeason))) + "E" + str(self.getNumberString(int(episode)))
        possibles.append(name)
        name = str(self.getNumberString(int(self.seriesSeason))) + "x" + str(self.getNumberString(int(episode)))
        possibles.append(name)
        return possibles

    def getCurrentFileNames(self, fileLocation):
        self.fileLocation = fileLocation
        fileExtensions = dict()
        self.currentFiles = os.listdir(self.fileLocation)
        for files in self.currentFiles:
            extensions = os.path.splitext(files)[1]
            if self.subtitleExists is False and extensions == ".srt":
                self.subtitleExists = True
            if self.mediaExtension == "" and extensions in [".mkv", ".mp4"]:
                self.mediaExtension = extensions
            
            if self.subtitleExists == True and self.mediaExtension != "":
                break

        if self.mediaExtension == "":
            print "ERROR : Could not get media extensions!"
            return

        if self.subtitleExists == False:
            print "ERROR : No subtitles"
            return

        print self
        #print(json.dumps(fileExtensions, index = 2))

    def scanForMachingFiles(self, wikipage, fileLocation):
        self.getCurrentFileNames(fileLocation)
        self.downloadEpisodeName(wikipage)
        self.constrctFileName()

        for key in self.seriesEpisodeNames:
            possibleMatches = self.seriesEpisodeNames[key][3]
            #print possibleMatches
            for fileName in self.currentFiles:
                #print possibleMatches[0]
                if re.search(possibleMatches[0], fileName):
                    extension = os.path.splitext(fileName)[1]
                    if extension == ".srt":
                        self.seriesEpisodeNames[key][6] = fileName
                    elif extension == self.mediaExtension:
                        self.seriesEpisodeNames[key][5] = fileName
                    else:
                        print "ERROR : Unknown File"
                if re.search(possibleMatches[1], fileName):
                    extension = os.path.splitext(fileName)[1]
                    if extension == ".srt":
                        self.seriesEpisodeNames[key][6] = fileName
                    elif extension == self.mediaExtension:
                        self.seriesEpisodeNames[key][5] = fileName
                    else:
                        print "ERROR : Unknown File"
                #else:
                #    print fileName
        print(json.dumps(self.seriesEpisodeNames, indent = 2))

    def changeMactchingFile(self, wikipage, fileLocation):
        self.scanForMachingFiles(wikipage, fileLocation)

        for key in self.seriesEpisodeNames:
            actualMediaFile = fileLocation + "/" + self.seriesEpisodeNames[key][5]
            newMediaFile = fileLocation + "/" + self.seriesEpisodeNames[key][2] + self.mediaExtension
            self.changeFileName(actualMediaFile, newMediaFile)

            if self.subtitleExists == True:
                actualSrtFile = fileLocation + "/" + self.seriesEpisodeNames[key][6]
                newSrtFile = fileLocation + "/" + self.seriesEpisodeNames[key][2] + ".srt"
                self.changeFileName(actualSrtFile, newSrtFile)

    def changeFileName(self, actualName, newName):
        print "Renaming : " + newName
        time.sleep(0.25)
        os.rename(actualName, newName)


def main():
    parser = OptionParser(usage = "USAGE : syncFiles.py <Mode> <Option> <Arguemnts>")
    parser.add_option("", "--wikipage",
            help="Wikipedia page to get the episode names!")
    parser.add_option("", "--series",
            help="Series Name to be considered!")
    parser.add_option("", "--season",
            help="Season of the series!")
    parser.add_option("", "--fileLocation",
            help="Location where media files are present!")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("Specify a mode!")
    mode = args[0]
    valid_modes = ['DownloadEpisodeNames', 'ConstructEpisodeNames', 'GetCurrentFileNames', 'ScanForMatchingFiles', 'ChangeMatchingFiles']
    if mode not in valid_modes:
        raise Exception("Following Modes supported!\n"
                        "DownloadEpisodeNames\n"
                        "ConstructEpisodeNames\n"
                        "ScanForMatchingFiles\n"
                        "ChangeMatchingFiles\n"
                        "GetCurrentFileNames\n")
    else:
        if not options.series or not options.season:
            parser.error("Series Name and Season mandatory!")
        else:
            sync = syncFiles(options.series, options.season)
            if mode == "DownloadEpisodeNames":
                if not options.wikipage:
                    parser.error("Specify the wikipedia page!")
                else:
                    print options.wikipage
                    sync.downloadEpisodeName(options.wikipage)
            if mode == "ConstructEpisodeNames":
                if not options.wikipage:
                    parser.error("Specify the wikipedia page!")
                else:
                    print options.wikipage
                    sync.downloadEpisodeName(options.wikipage)
                    sync.constrctFileName()
            if mode == "GetCurrentFileNames":
                if not options.fileLocation:
                    parser.error("Specify the file Location!")
                else:
                    print options.fileLocation
                    sync.getCurrentFileNames(options.fileLocation)
            if mode == "ScanForMatchingFiles":
                if not options.fileLocation:
                    parser.error("Specifiy the file Location!")
                elif not options.wikipage:
                    parser.error("Specify the wikipedia page!")
                else:
                    print options.wikipage
                    print options.fileLocation
                    sync.scanForMachingFiles(options.wikipage, options.fileLocation)
            if mode == "ChangeMatchingFiles":
                if not options.fileLocation:
                    parser.error("Specifiy the file Location!")
                elif not options.wikipage:
                    parser.error("Specify the wikipedia page!")
                else:
                    print options.wikipage
                    print options.fileLocation
                    sync.changeMactchingFile(options.wikipage, options.fileLocation)


if __name__ == "__main__":
    main()
