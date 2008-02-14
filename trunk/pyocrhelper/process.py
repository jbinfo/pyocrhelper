from moduleFunctions import config
import subprocess,re

class process:
    def __init__(self):
        self.defaults = config().defaults
        self.raw = []

    def doOcrScan(self,list):
        """ Perform the ocr scan on each input image and concat
            the results of the scan to a single string
        """
        text = ""
        for img in list:
            try:
                text = subprocess.Popen([r"%s"%self.defaults['ocrBin'],\
                            img ],\
                            stdout=subprocess.PIPE,\
                            stderr=subprocess.PIPE).communicate()[0]
            except Exception,e:
                print e
                # raise exception
            else:
                self.raw.append(text)
        return sorted(self.raw)

    def concat(self):
        """
        Refactor some code from formatResults which is needed
        to concatenate multiple pages into one.
        Returns one large html page
        """
        re_page1 = re.compile(r'(?P<page1>.*)</body>.*',re.S)
        re_pagex = re.compile(r'.*<body>(?P<pagex>.*)</body>.*',re.S)
        re_pagen = re.compile(r'.*<body>(?P<pagen>.*)',re.S)
        centre = ""
        if len(self.raw) == 1:
            return self.raw[0]
        elif len(self.raw)==2:
            strip_page_1 = re.search(re_page1,self.raw[0])
            if strip_page_1:
                stripped_1 = strip_page_1.group('page1')
            else: print "Failed to isolate page 1 stucture"
            strip_page_2 = re.search(re_pagen,self.raw[1])
            if strip_page_2:
                stripped_2 = strip_page_2.group('pagen')
            else: print "Failed to isolate page 2 structure"
            return "%s\n<!-- Page Break -->\n%s"%(stripped_1,stripped_2)
        else:
            strip_page_1 = re.search(re_page1,self.raw[0])
            if strip_page_1:
                stripped_1 = strip_page_1.group('page1')
            else: print "Failed to isolate page 1 structure"
            strip_page_n = \
                re.search(re_pagen,self.raw[len(self.raw)-1])
            if strip_page_n:
                stripped_n = strip_page_n.group('pagen')
            else: print "Failed to isolate page n structure"
            for page in self.raw[1:len(self.raw)-2]:
                strip_page_x = re.search(re_pagex,page)
                if strip_page_x:
                    centre = \
                    "<!-- Page Break -->%s"%centre+strip_page_x.group('pagex')
                else: print "Failed to isolate page x structure"
            return "%s%s%s"%(stripped_1,centre,stripped_n)
