import re
from itertools import count,izip
from operator import itemgetter
class analyse:
    """ Code to perform actual page/line analysis refactored here """

    def __init__(self):
        """
        Analyses a page output by ocropus
        """
        self.page = "" 
        self.gaps = []
        self.lx,self.ty,self.rx,self.by = [],[],[],[] # lists for coord type
        self.max_l = 0 # leftmost x coordinate (on page)
        self.max_t = 0 # topmost y coordinate (on page)
        self.max_r = 0 # rightmost x coordinate (on page)
        self.max_b = 0 # bottommost y coordinate (on page)

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


    def weight(self,a, b, int_max):
        if int_max <=0:
            if a==b: return 1
            else: return 0
        if a > b : d = a - b
        else: d = b -a
        if d > int_max : return 0
        return 1-(d/int_max)

    def blur(self,list,factor=0.1):
        lbound,hbound = int(min(list)),int(max(list))
        spread = int(factor * (hbound-lbound))
        s = []
        for x in range((lbound-spread),(hbound+spread)):
            sum = 0
            for i in list:
                sum += self.weight(x,i,spread)
            s.append((x,sum))
        return s

    def group(self,maxima,list):
        """
        Group the weighed clusters by cluster and include
        data on cluster average and cluster variance
        Accepts 2 lists whereby maxima is a list of dicts
        Returns dictionary
        """
        mdict = {}
        for a in list:
            best = -1
            dist = 0xfffffff
            for m in maxima:
                d = (m[0]-a)
                if d < 0 : d = -d
                if d < dist:
                    dist = d
                    best = m[0]
            if not mdict.has_key(best):
                mdict[best] = {"n":0,"sum":0,"sumsq":0}
            mdict[best]["n"] += 1
            mdict[best]["x"] = best
            mdict[best]["sum"] += a
            mdict[best]["sumsq"] += a**2
            if not mdict[best].has_key("min") : mdict[best]["min"] = a
            if a < mdict[best]["min"] : mdict[best]["min"] = a
            if not mdict[best].has_key("max") : mdict[best]["max"] = a
            if a > mdict[best]["max"] : mdict[best]["max"] = a

        for y in [v for k,v in enumerate(mdict)]: # list of dicts
            avg = mdict[y]["sum"]/mdict[y]["n"]
            avgsq = mdict[y]["sumsq"]/mdict[y]["n"]
            mdict[y]["avg"] = int(avg)
            mdict[y]["var"] = avgsq - (mdict[y]["avg"]*mdict[y]["avg"])
            del(mdict[y]["x"])
            del(mdict[y]["sumsq"])
            del(mdict[y]["sum"])

        return mdict

    def doAnalysis(self,list):
        blurred = self.blur(list)
        maxima = []
        m = (0,0) #???
        rising = 1
        for i in range(0,len(blurred)-1):
            if blurred[i][1] > m[1]:
                rising = 1
            if blurred[i][1] < m[1]:
                if rising != 0: maxima.append(m)
            rising = 0
            m = blurred[i]
        return self.group(maxima,list)

    def analysePage(self,page):
        self.page = page
        self.getData()
        self.analyse_lx = self.doAnalysis(self.lx)
        self.analyse_rx = self.doAnalysis(self.rx)
        self.analyse_ty = self.doAnalysis(self.ty)
        self.analyse_by = self.doAnalysis(self.by)
        self.analyse_gaps = self.doAnalysis(self.gaps)
