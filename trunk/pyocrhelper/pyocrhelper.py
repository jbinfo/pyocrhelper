import sys,os,re,time,subprocess
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
            (ppms) are temporarily stored in self.tmpdir. Note that
            increasing dpi from pdftoppm's default 150 to ocropus's
            preferred 300 yields noticeable quality improvements
        """
        fnamebase = os.path.join(self.defaults['tmpdir'],self.inputFileName)
        try:
            subprocess.Popen([r"pdftoppm","-r","300",\
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

