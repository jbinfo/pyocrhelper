#!/usr/bin/env python
from pyocrhelper.input import input
from pyocrhelper.process import process
from pyocrhelper.analyse import analyse
from pyocrhelper.output import output
import sys,os

def usage():
    print
    print "    This is a test script for the pyocrhelper module"
    print "    Usage: %s <inputfile> [outputfile] [format]"%sys.argv[0]
    print "    Example: %s /tmp/test.pdf /tmp/test.html"%sys.argv[0]
    print "    Example: %s /tmp/test.pdf txt >> /tmp/test.txt"%sys.argv[0]
    print
    
#usage()

inputFile,outputFile,method = None,None,None

if len(sys.argv) != 3:
    print "You have to provide two arguments to this script"
    sys.exit(1) # are there exactly 2 arguments?

# Does the input file exist and do we have permission to read it?
if not os.path.isfile(os.path.abspath(sys.argv[1])):
    print "%s does not exist"%os.path.abspath(sys.argv[1])
    sys.exit(1)
elif not os.access(os.path.abspath(sys.argv[1]),os.R_OK):
    print "No permission to read %s"%os.path.abspath(sys.argv[1])
    sys.exit(1)
else:
    inputFile = os.path.abspath(sys.argv[1])

# Is the 2nd argument a file or an output method?
if sys.argv[2] in ['txt','html']: method = 'return'
else:
    if not os.access(os.path.dirname(sys.argv[2]),os.W_OK):
        print "No permission to write output file %s in %s"%(\
                os.path.basename(sys.argv[2]),\
                os.path.dirname(os.path.abspath(sys.argv[2])))
        sys.exit(1)
    else:
        method = 'file'
        outputFile = os.path.abspath(sys.argv[2])

inp = input(inputFile)
list = inp.prepareListForOcr()
ocr = process()
raw = ocr.doOcrScan(list)
pageHolder = []
doctor = analyse()
for page in raw:
    pageLayout = {}
    pageinfo = doctor.analysePage(page)
    pageLayout =    {
                    'gaps_analysis':doctor.analyse_gaps,
                    'max_l':doctor.max_l,
                    'max_t':doctor.max_t,
                    'max_r':doctor.max_r,
                    'max_b':doctor.max_b,
                    'lx_analysis':doctor.analyse_lx,
                    'ty_analysis':doctor.analyse_ty,
                    'rx_analysis':doctor.analyse_rx,
                    'by_analysis':doctor.analyse_by,
                    'page_text':page
                    }
    pageHolder.append(pageLayout)
outputter = output(pageHolder)
outputter.stripFirst()
outputter.stripLast()
outputter.stripCentre()
for i in pageHolder:
    print i['page_text']
