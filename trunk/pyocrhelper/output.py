from moduleFunctions import config
from analyse import analyse
import re,sys

class output:

    def __init__(self,pagelist):
        self.defaults = config().defaults
        self.pages = pagelist

    def stripFirst(self):
        re_first = re.compile(r'(?P<page1>.*)</body>.*',re.S)
        search = re.search(re_first,self.pages[0]['page_text'])
        gaps = self.pages[0]['gaps_analysis']
        #gaps is a list of dicts
        smallest_av = (0,99999)
        for x in gaps:
            if x['avg']<smallest_av[1]:
                smallest_av = (gaps.index(x),x['avg'])
        avg_lower_range = gaps[smallest_av[0]]['min']
        avg_upper_range = gaps[smallest_av[0]]['max']
        if search:
            content = search.group('page1')
            last_y = 0
            lines_with_br = ""
            for line in content.split('\n'):
                coords = analyse().getCoordinates(line)
                if coords:
                    if last_y != 0:
                        whitespace_above = int(coords[1])-last_y
                        # this is where the decision <br> or <p> is made
                        #print whitespace_above, avg_upper_range
                        if whitespace_above <= avg_upper_range and whitespace_above >= avg_lower_range:
                            lines_with_br = lines_with_br+"<br/>%s"%line
                        else:
                            lines_with_br = lines_with_br+"<br/><br/>%s"%line
                    last_y = int(coords[3])
                else:
                    lines_with_br = lines_with_br+line
            self.pages[0]['page_text'] = lines_with_br

    def stripLast(self):
        re_last = re.compile(r'.*<body>(?P<pagen>.*)',re.S)
        search = re.search(re_last,\
                self.pages[len(self.pages)-1]['page_text'])
        if search:
            content = search.group('pagen')
            last_y = 0
            lines_with_br = ""
            for line in content.split('\n'):
                coords = analyse().getCoordinates(line)
                if coords:
                    if last_y != 0:
                        whitespace_above = int(coords[2])-last_y
                        last_y = int(coords[3])
                    lines_with_br = lines_with_br+"%s<br/>"%line
                else:
                    lines_with_br = lines_with_br+line
            self.pages[len(self.pages)-1]['page_text']\
                 = lines_with_br

    def stripCentre(self):
        re_centre = \
                re.compile(r'.*<body>(?P<pagex>.*)</body>.*',re.S)
        for centrepages in self.pages[1:len(self.pages)-2]:
            search = re.search(re_centre,centrepages['page_text'])
            if search:
                content = search.group('pagex')
                indexof = self.pages.index(centrepages)
                last_y = 0
                lines_with_br = ""
                for line in content.split('\n'):
                    coords = analyse().getCoordinates(line)
                    if coords:
                        if last_y != 0:
                            whitespace_above = int(coords[2])-last_y
                            last_y = int(coords[3])
                        lines_with_br = lines_with_br+"%s<br/>"%line
                    else:
                        lines_with_br = lines_with_br+line
                self.pages[indexof]['page_text']\
                     = lines_with_br

	    
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
        text = self._concat()
        if self.outputFileFormat == ".txt":
            return self.html2txtwrapper(text)
        else:
            return text

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
