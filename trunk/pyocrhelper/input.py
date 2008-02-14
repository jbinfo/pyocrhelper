from moduleFunctions import config
import os,re,subprocess
from PIL import Image
class input:

    def __init__(self,inputFile):
        self.defaults = config().defaults
        self.inputFile = inputFile
        self.inputFileName = os.path.basename(self.inputFile)
        self.inputFileDir = os.path.dirname(self.inputFile)
        self.pdfinfo = {} # holds pdfinfo if needed
        self.rawImageHolder = [] # holds imgs for converting
        self.preparedImages = [] # hold imgs ready for ocr
        self.inputFileFormat = "" # placeholder for format

    def prepareListForOcr(self):
        """ Use class methods to prepare input file for processing """
        try:
            self.inputFileFormat = self.getInputFormat()
        except:
            print "could not determine file format" # raise exception
        if self.inputFileFormat == 'PDF': self.pdfToImages()
        else: self.rawImageHolder.append(self.inputFile)
        # do not waste time converting if input is already target
        if self.inputFileFormat.lower() != self.defaults['ocrImgFmt']:
            self.convertToTargetFormat()
        else:
            self.preparedImages.append(self.inputFile)
        return self.preparedImages

    def getInputFormat(self):
        """ Determine the incoming file type. If the filetype
            is not allowed raise appropriate error.
        """
        try:
            im = Image.open(self.inputFile)
        except Exception,e:
            if str(e).lower() == "cannot identify image file":
                re_pages = \
                    re.compile(r'Pages:\s*\b(?P<pages>.*)')
                pdfinfostatus = subprocess.Popen([r"pdfinfo",\
                        self.inputFile],\
                        stdout=subprocess.PIPE,\
                        stderr=subprocess.PIPE).wait()
                if pdfinfostatus != 0:
                    return None
                else:
                    pdfinfo = subprocess.Popen([r"pdfinfo",\
                        self.inputFile],\
                        stdout=subprocess.PIPE,\
                        stderr=subprocess.PIPE).communicate()[0]
                    probe_pages = re.search(re_pages,pdfinfo)
                    if probe_pages:
                        self.pdfinfo["pages"] =int(probe_pages.group('pages'))
                    else:
                        self.pdfinfo["pages"] = 0
                    return 'PDF'
        else:
            return im.format

    def pdfToImages(self):
        """ If a pdf is recognised, convert the pages to images
            using a pdftoimages subprocess. The images generated
            (ppms) are temporarily stored in self.tmpdir. Note that
            increasing dpi from pdftoppm's default 150 to ocropus's
            preferred 300 yields noticeable quality improvements
        """
        fnamebase = os.path.join(self.defaults['tmpDir'],self.inputFileName)
        try:
            subprocess.Popen([r"pdftoppm","-r","300",\
                            self.inputFile,fnamebase ],\
                            stdout=subprocess.PIPE,\
                            stderr=subprocess.PIPE).communicate()[0]
        except Exception,e:
            print e
            return None
        readProcessed = os.listdir(self.defaults['tmpDir'])
        # the images have to be properly sorted or we will run into trouble!
        # this method is probably not very safe but it mostly works
        imgDict = {}
        i = 1
        len_inputFileName = len(self.inputFileName)
        while i <= len(readProcessed):
            for img in readProcessed:
                if img.endswith('.ppm'): # prevents problems if dir not clean
                    img_idx = int(img[len(img)-10:len(img)-4])
                    if img_idx == i and img[:len_inputFileName]\
                     == self.inputFileName:
                        imgDict[i] = img
            i += 1
        for a in imgDict.keys():
            self.rawImageHolder.append(os.path.join(self.defaults['tmpDir'],imgDict[a]))
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
                save_as_base = os.path.join(self.defaults['tmpDir'],\
                                os.path.basename(img))
                if os.path.basename(img).endswith(self.defaults['ocrImgFmt']):
                    save_as = save_as_base
                else:
                    save_as = \
                        "%s.%s"%(save_as_base,self.defaults['ocrImgFmt'])
                try:
                    apply(im.save, (save_as,), options)
                except Exception,e:
                    print e
                    sys.stderr.write("%s\n"%e)
                    return None
                    # raise exception
                else:
                    self.preparedImages.append(save_as)
