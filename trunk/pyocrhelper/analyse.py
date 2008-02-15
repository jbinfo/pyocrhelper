import re
from itertools import count,izip
from operator import itemgetter

class analyse:

    def __init__(self):
        self.page = ""
        self.gaps = []
        self.lx,self.ty,self.rx,self.by = [],[],[],[] # lists for coord type
        self.max_l = 0 # leftmost x coordinate (on page)
        self.max_t = 0 # topmost y coordinate (on page)
        self.max_r = 0 # rightmost x coordinate (on page)
        self.max_b = 0 # bottommost y coordinate (on page)

    def weight(self,a,b,max):
        d = 0.0
        if max <= 0:
            if a == b: return 1
            else: return 0

        if a > b: d = a-b
        else: d = b-a

        if d >= max: return 0
        else:
            return float(1.0-(float(d)/float(max)))

    def blur(self,arr,factor=0.1):
        lbound,hbound = min(arr),max(arr)
        spread = int(0.5 * factor * (hbound-lbound))
        slist = []
        for x in range((lbound-spread),(hbound+spread)):
            s = 0
            for i in arr:
                s += self.weight(x,i,spread)
            slist.append((x,s))
        return slist

    def group(self,ma,arr):
        m = {}
        list = []
        for a in arr:
            best = -1
            dist = 0xfffffff
            for mt in ma:
                d = mt[0]-a
                if d < 0: d = -d
                if d < dist:
                    dist = d
                    best = mt[0]
            if not m.has_key(best):
                m[best] = {'n':0,'x':0,'sum':0,'sumsq':0}
            m[best]['n'] = m[best]['n'] + 1
            m[best]['x'] = best
            m[best]['sum'] = m[best]['sum'] + a
            m[best]['sumsq'] = m[best]['sumsq'] **2
            if not m[best].has_key('min'):
                m[best]['min'] = a
            else:
                if a < m[best]['min']: m[best]['min'] = a
            if not m[best].has_key('max'):
                m[best]['max'] = a
            else:
                if a > m[best]['max']: m[best]['max'] = a

        for x in m.keys():
            avg = m[x]['sum']/m[x]['n']
            avgsq = m[x]['sumsq']/m[x]['n']
            m[x]['avg'] = int(avg)
            m[x]['var'] = avgsq-(m[x]['avg']**2)
            del(m[x]['x'])
            del(m[x]['sumsq'])
            del(m[x]['sum']) 
        # return a list to stay as compatible as possible with ocrocol.py
        for x in m.keys():
            list.append(m[x])
        return list
    

    def getCoordinates(self,line):
        """
        Use a regular expression to extract the page coordinates
        from a typical hOcr string. This automatically extracts
        only the content lines from the html outputs
        Returns a tuple
        """
        getdigits = \
        re.compile(r'bbox\s+?(?P<pos1>\d{1,4})\s+?(?P<pos2>\d{1,4})\s+?(?P<pos3>\d{1,4})\s+?(?P<pos4>\d{1,4})'\
            ,re.S)
        a = re.search(getdigits,line)
        if not a:
            return None
        else:
            return (int(a.group('pos1')),int(a.group('pos2')),\
                    int(a.group('pos3')),int(a.group('pos4')))

    def getData(self):
        """
        The getData method is responsible for parsing the raw statistical
        output into lists which can in turn be parsed and balanced using
        the cluster analyser.
        """
        lines = self.page.split('\n')
        hanging = 0
        coord = ()
        for line in lines:
            coord = self.getCoordinates(line)
            if coord:
                # Get the max left,top,right,bottom page coordinates
                if coord[0] > self.max_l: self.max_l = coord[0]
                if coord[1] > self.max_t: self.max_t = coord[1]
                if coord[2] > self.max_r: self.max_r = coord[2]
                if coord[3] > self.max_b: self.max_b = coord[3]
                # Determine the gap to the previous horizontal line
                if int(coord[1]) > hanging:
                    self.gaps.append(int(coord[1]-hanging))
                # Split the coordinates into lists
                self.lx.append(coord[0])
                self.ty.append(coord[1])
                self.rx.append(coord[2])
                self.by.append(coord[3])
                hanging = int(coord[3])

    def doAnalysis(self,list):
        blist = self.blur(list)
        maxima = []
        m = (0,0)
        rising = 1
        for i in range(0,len(blist)):
            if blist[i][1] > m[1]:
                rising = 1
            if blist[i][1] < m[1]:
                if rising:
                    maxima.append(m)
                    rising = 0
            m = blist[i]
        return self.group(maxima,list)

    def analysePage(self,page):
        self.page = page
        self.getData()
        self.analyse_lx = self.doAnalysis(self.lx)
        self.analyse_rx = self.doAnalysis(self.rx)
        self.analyse_ty = self.doAnalysis(self.ty)
        self.analyse_by = self.doAnalysis(self.by)
        self.analyse_gaps = self.doAnalysis(self.gaps)
        return True
