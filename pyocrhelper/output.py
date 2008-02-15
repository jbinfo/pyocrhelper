from moduleFunctions import config
from analyse import analyse
import re,sys

class output:

    def __init__(self):
        self.defaults = config().defaults
        self.pages = []
    
    def output(self,pagelist):
        self.pages = pagelist
        if len(self.pages)==1:
            self.stripFirst(1)
        else:
            self.stripFirst()
            if len(self.pages) == 2:
                self.stripLast()
            else:
                self.stripCentre()
                self.stripLast()
        return self.pages

    def formatLineBreaks(self,page_info):
        """ Consolidate code for creating line breaks here """
        # determine the 'normal' line break
        gaps = page_info['gaps_analysis']
        smallest_average_gap = (0,0)
        largest_average_gap = (0,0)
        most_frequent_gap = (0,0)
        for i in gaps: # loop through the dictionaries
            if i['n'] > most_frequent_gap:
                most_frequent_gap = (i,i['n']) # taking this to be 'normal'
        lower = gaps[most_frequent_gap[0]]['min'] # lower boundary
        upper = gaps[most_frequent_gap[0]]['max'] # upper boundary
        previous_y = 0
        string = ""
        for line in page_info['stripped_text']:
            coords = analyse().getCoordinates(line)
            if not  coords:
                string = string+line
            else:
                top_y = int(coords[1])
                if previous_y != 0: # skip the first iteration
                    whitespace = int(top_y-previous_y)
                    if whitespace >= lower and whitespace <= upper:
                        string = string+"<br/>%s"%line
                    elif whitespace > upper:
                        string = string+"<br/><br/>%s"%line
                    else:
                        string = string+line # not quite sure what this does
                previous_y = int(coords[3]) # our bottom y is now 'previous'
        return string




    def stripFirst(self,none_following=0):
        """
        If none_following is set to 1 by the calling script, then
        this method does not attempt to strip the closing body and
        html tags. Otherwise it does
        """
        re_first = re.compile(r'(?P<page1>.*)</body>.*',re.S)
        if none_following == 0:
            search = re.search(re_first,self.pages[0]['page_text'])
        else:
            search = True
        if search:
            if none_following == 0:
                content = search.group('page1')
            else:
                content = self.pages[0]['page_text']
            page_info = {   'gaps_analysis':self.pages[0]['gaps_analysis'],
                            'stripped_text':content
                        }
            self.pages[0]['page_text'] = self.formatLineBreaks(page_info)

    def stripLast(self):
        re_last = re.compile(r'.*<body>(?P<pagen>.*)',re.S)
        search = re.search(re_last,\
                self.pages[len(self.pages)-1]['page_text'])
        if search:
            content = search.group('pagen')
            page_info = {   
             'gaps_analysis':self.pages[len(self.pages)-1]['gaps_analysis'],
             'stripped_text':content
                        }
            self.pages[len(self.pages)-1]['page_text'] = \
                self.formatLineBreaks(page_info)

    def stripCentre(self):
        re_centre = \
                re.compile(r'.*<body>(?P<pagex>.*)</body>.*',re.S)
        for centrepages in self.pages[1:len(self.pages)-2]:
            search = re.search(re_centre,centrepages['page_text'])
            if search:
                content = search.group('pagex')
                indexof = self.pages.index(centrepages)
                page_info = {
                   'gaps_analysis':self.pages[indexof]['gaps_analysis'],
                   'stripped_text':content
                            }
                self.pages[indexof]['page_text'] = \
                    self.formatLineBreaks(page_info)

	    
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
