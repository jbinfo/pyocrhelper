#!/usr/bin/env python
import sys,os,re,time,subprocess,shutil
# import config # not needed in v0.1
from PIL import Image

class pyocrhelper:

    def __init__(self,inputFile,outputFile="",outputFileFormat=""):
        """ Initialise with an input and optionally output
            file. Read configuration.
        """
        self.rawText = []
        self.rawImageHolder = [] # hold images before converting to target
        self.readyImageHolder = [] # hold images ready for ocr
        self.defaults = self.getDefaultsFromConfig()
        self.clearTmp() # clear up the tmp directory before anything gets done
        self.pdfinfo = {} # will be filled if input is pdf
        self.allowed_fmt = ['.html','.txt']
        self.inputFileAbspath = os.path.abspath(inputFile)
        self.inputFileName = os.path.basename(self.inputFileAbspath)
        self.inputFileFormat = self.getFileType()
        if outputFile == "":
            self.outputMethod = "return"
            self.outputFileAbspath = ""
            self.outputFileName = ""
            
        else:
            self.outputMethod = "file"
            self.outputFileAbspath = os.path.abspath(outputFile)
            self.outputFileName = os.path.basename(self.outputFileAbspath)
        self.outputFileFormat = self.getOutputFormat(outputFileFormat)
        if self.inputFileFormat == "pdf": # we need to get images first
            self.pdfToImages()
        else:
            self.rawImageHolder.append(self.inputFileAbspath)
        self.convertToTargetFormat()
        self.doOcrScan()
        self.formattedText = self.formatResults()
        if self.outputMethod == "return":
            self.write = self.formattedText
        else:
            if self.writeToDisk():
                self.write = self.outputFileAbspath
            else:
                self.write = None

    def _testSetup(self):
        """
        Check the setup:
            - is ocropus present?
            - is pdftoppm present?
            - is PIL present?
        """
        pass

    def clearTmp(self):
        """ Remove all files from temporary directory
            Typically called before starting and after finishing
        """
        contents = os.listdir(self.defaults['tmpdir'])
        if len(contents)==0:
            return True
        for i in contents:
            path_to_i = os.path.join(self.defaults['tmpdir'],i)
            if os.path.isfile(path_to_i):
                try:
                    os.unlink(path_to_i)
                except Exception,e:
                    print e
                    # raise exception
            elif os.path.isdir(path_to_i):
                try:
                    shutil.rmtree(path_to_i)
                except Exception,e:
                    print e
                    # raise exception

    def getDefaultsFromConfig(self):
        """ Read in the configuration from the config module and
            sort the values into a dictionary.

            Note that reading in config from config.py is disabled
            in v0.1 as it is really unnecessary for 4 vars. However,
            leaving the code in is a good idea so we can scale up
            if needed.
        """
        defaultsDict = {}
        defaultsDict['tmpdir'] = \
                    "/tmp/pyocrhelper/"
        defaultsDict['outputFileFormat'] = \
                    "html"
        defaultsDict['ocrInputFormat'] = \
                    "png"
        defaultsDict['ocrLocation'] = \
                    "/usr/bin/ocropus"
        return defaultsDict
        #try:
            #readConfig = config.Start()
        #except Exception,e:
        #    print e # raise exception
        #defaultsDict = {}
        #defaultsDict['tmpdir'] = \
        #            "/tmp/pyocrhelper/"
        #            #readConfig.tmpdir
        #defaultsDict['outputFileFormat'] = \
        #            "html"
        #            #readConfig.outputFileFormat
        #defaultsDict['ocrInputFormat'] = \
        #            "png"
        #            #readConfig.ocrInputFormat
        #defaultsDict['ocrLocation'] = \
        #            "/usr/bin/ocropus"
        #            #readConfig.ocrLocation
        #return defaultsDict

    def getOutputFormat(self,outputFileFormat):
        """ Determine the output format by looking at the
            (1). outputFileFormat
            (2). if not (1) then look at outputFile extension
            (3). if not (2) then look at default from config
        """
        if outputFileFormat != "" and outputFileFormat != None:
            if outputFileFormat.lower() in self.allowed_fmt:
                return outputFileFormat.lower()
            else:
                # raise exception
                print "Unrecognised output format %s"%outputFileFormat
        else:
            if self.outputFileName != None and self.outputFileName != "":
                # see if we can determine the fileformat from the extension
                if len(self.outputFileName.split('.'))==1:
                    return self.defaults['outputFileFormat']
                else:
                    for i in range(2, 0, -1):
                        fparts = self.outputFileName.rsplit(".", i)
                        if len(fparts) == 3:
                            extension = "." + fparts[1] + "." + fparts[2]
                        elif len(fparts) == 2:
                            extension = "." + fparts[1]
                    if extension.lower() in self.allowed_fmt:
                        return extension.lower()
                    else:
                        print "unrecognised extension %s"%extension
                        # raise exception
                        return None
            else:
                return self.defaults['outputFileFormat']

    def getFileType(self):
        """ Determine the incoming file type. If the filetype
            is not allowed raise appropriate error.
        """
        try:
            im = Image.open(self.inputFileAbspath)
        except Exception,e:
            # this sucks. find a more solid way of doing this
            if re.match('.*cannot identify image file.*',str(e),re.I):
                re_notpdf = re.compile(r'Error.*',re.M)
                re_author = \
                    re.compile(r'Author:\s*\b(?P<author>.*)')
                re_pages = \
                    re.compile(r'Pages:\s*\b(?P<pages>.*)')
                re_version = \
                    re.compile(r'PDF version:\s*\b(?P<version>.*)')
                try:
                    allinfo = subprocess.Popen([r"pdfinfo",\
                            self.inputFileAbspath],\
                            stdout=subprocess.PIPE,\
                            stderr=subprocess.PIPE).communicate()[0]
                            # communicate() returns tuple of stdout,stderr
                except Exception,e:
                    # note that pdfinfo doesn't raise an error even if
                    # the file is not a pdf - it continues anyway
                    print e
                else:
                    notpdf = re.search(re_notpdf,allinfo)
                    if notpdf:
                        # raise exception
                        print "that wasn't a pdf"
                        return None
                    else:
                        pages = re.search(re_pages,allinfo)
                        if pages:
                            self.pdfinfo['pages'] = int(pages.group('pages'))
                        else:
                            self.pdfinfo['pages'] = 0
                        author = re.search(re_author,allinfo)
                        if author:
                            self.pdfinfo['author'] = str(author.group('author'))
                        else:
                            self.pdfinfo['author'] = "No author found"
                        version = re.search(re_version,allinfo)
                        if version:
                            self.pdfinfo['version'] = str(version.group('version'))
                        else:
                            # is it ok for a pdf to have no version?
                            # raise exception
                            print "No pdf version name received - probably a buggy pdf"
                            return None
                            self.pdfinfo['version'] = "No version found"
                        return "pdf"
        else:
            return im.format

    def pdfToImages(self):
        """ If a pdf is recognised, convert the pages to images
            using a pdftoimages subprocess. The images generated
            (ppms) are temporarily stored in self.tmpdir
        """
        fnamebase = os.path.join(self.defaults['tmpdir'],self.inputFileName)
        try:
            subprocess.Popen([r"pdftoppm",\
                            self.inputFileAbspath,fnamebase ],\
                            stdout=subprocess.PIPE,\
                            stderr=subprocess.PIPE).communicate()[0]
        except Exception,e:
            print e
            return None
        readProcessed = os.listdir(self.defaults['tmpdir'])
        # the images have to be properly sorted or we will run into trouble!
        # this method is probably not very safe but it mostly works
        imgDict = {}
        i = 1
        while i <= len(readProcessed):
            for img in readProcessed:
                img_idx = int(img[len(img)-10:len(img)-4])
                if img_idx == i:
                    imgDict[i] = img
            i += 1
        for a in imgDict.keys():
            self.rawImageHolder.append(os.path.join(self.defaults['tmpdir'],imgDict[a]))
        return True

    def convertToTargetFormat(self):
        """ For each image found or converted, now convert the
            image to the target format - which is the preferred
            input format of the ocr software
        """
        options = {'optimize':1}
        iter = 0
        for img in self.rawImageHolder:
            try:
                im = Image.open(img)
            except Exception,e:
                sys.stderr.write("%s\n"%e)
                print e
                return None
                # raise exception
            else:
                try:
                    save_as = "%s.%s"%(img,self.defaults['ocrInputFormat'])
                    apply(im.save, (save_as,), options)
                except Exception,e:
                    print e
                    sys.stderr.write("%s\n"%e)
                    return None
                    # raise exception
                else:
                    self.readyImageHolder.append(save_as)

    def doOcrScan(self):
        """ Perform the ocr scan on each input image and concat
            the results of the scan to a single string
        """
        text = ""
        for img in self.readyImageHolder:
            try:
                text = subprocess.Popen([r"%s"%self.defaults['ocrLocation'],\
                            os.path.abspath(img) ],\
                            stdout=subprocess.PIPE,\
                            stderr=subprocess.PIPE).communicate()[0]
            except Exception,e:
                print e
                # raise exception
            else:
                self.rawText.append(text)
        sorted(self.rawText)

    def html2txtwrapper(self,html):
        """
        Kind of overly aggressive function to convert html to text
        Found on http://snippets.dzone.com/tag/html2txt
        """
        p = re.compile('(<p.*?>)|(<tr.*?>)', re.I)
        t = re.compile('<td.*?>', re.I)
        comm = re.compile('<!--.*?-->', re.S)
        dtd = re.compile('<!DOCTYPE.*?>',re.S)
        tags = re.compile('<.*?>', re.M)

        def html2txt(s, hint = 'entity', code = 'ISO-8859-1'):
            """Convert the html to raw txt
            - suppress all return
            - <p>, <tr> to return
            - <td> to tab
            """
            #s = s.replace('\n', '')
            s = s.replace('OCR Output','')
            s = p.sub('\n', s)
            s = t.sub('\t', s)
            s = dtd.sub('', s)
            s = comm.sub('', s)
            s = tags.sub('', s)
            s = re.sub(' +', ' ', s)
            # handling of entities
            result = s
            pass
            return result
        return html2txt(html)

    def formatResults(self):
        """ Depending on the chosen output format convert the 
            concatenated string to the appropriate format
        """
        re_page1 = re.compile(r'(?P<page1>.*)</body>.*',re.S)
        re_pagex = re.compile(r'.*<body>(?P<pagex>.*)</body>.*',re.S)
        re_pagen = re.compile(r'.*<body>(?P<pagen>.*)',re.S)
        centre = ""
        if len(self.rawText) == 1:
            # check output format
            if self.outputFileFormat == ".txt":
                return self.html2txtwrapper(self.rawText[0])
            else:
                return self.rawText[0]
        elif len(self.rawText)==2:
            strip_page_1 = re.search(re_page1,self.rawText[0])
            if strip_page_1:
                stripped_1 = strip_page_1.group('page1')
            else: print "Failed to isolate page 1 stucture"
            strip_page_2 = re.search(re_pagen,self.rawText[1])
            if strip_page_2:
                stripped_2 = strip_page_2.group('pagen')
            else: print "Failed to isolate page 2 structure"
            if self.outputFileFormat == ".txt":
                return self.html2txtwrapper(\
                        "%s\n<!-- Page Break -->\n%s"%(stripped_1,stripped_2))
            else:
                return "%s\n<!-- Page Break -->\n%s"%(stripped_1,stripped_2)
        else:
            strip_page_1 = re.search(re_page1,self.rawText[0])
            if strip_page_1:
                stripped_1 = strip_page_1.group('page1')
            else: print "Failed to isolate page 1 structure"
            strip_page_n = \
                re.search(re_pagen,self.rawText[len(self.rawText)-1])
            if strip_page_n:
                stripped_n = strip_page_n.group('pagen')
            else: print "Failed to isolate page n structure"
            for page in self.rawText[1:len(self.rawText)-2]:
                strip_page_x = re.search(re_pagex,page)
                if strip_page_x:
                    centre = \
                    "<!-- Page Break -->%s"%centre+strip_page_x.group('pagex')
                else: print "Failed to isolate page x structure"
            if self.outputFileFormat == ".txt":
                return self.html2txtwrapper(\
                        "%s%s%s"%(stripped_1,centre,stripped_n))
            else:
                return "%s%s%s"%(stripped_1,centre,stripped_n)

    def writeToDisk(self):
        """ If output method is to write to file, open the file and write
            the text to it """
        try:
            open_write = open(self.outputFileAbspath,"w")
        except Exception,e:
            print e
            # raise exception
            return False
        else:
            open_write.write(self.formattedText)
            open_write.close
            return True

if __name__ == "__main__":
    
    if len(sys.argv)!=4:
        sys.stderr.write("   Usage: %s %s %s %s\n"%(sys.argv[0],\
                        "<input file>","[output file]","[format]"))
        sys.stderr.write("   Example: %s %s %s %s\n"%(sys.argv[0],\
                        "/home/user/test.pdf","/home/user/result.html","''"))
        sys.exit(1)
    
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
    outputFileFormat = sys.argv[3]

    if not os.path.isfile(os.path.abspath(inputFile)):
        sys.stderr.write("%s does not exist\n"%inputFile);sys.exit(1)
    elif not os.access(os.path.abspath(inputFile),os.R_OK):
        sys.stderr.write("No permission to read %s\n"%inputFile);sys.exit(1)
    else: pass

    try:
        a = pyocrhelper(inputFile,outputFile,outputFileFormat)
    except Exception,e:
        print e
    else:
        if a.outputMethod == "file":
            print "Written to %s"%a.write
        else:
            print a.write
