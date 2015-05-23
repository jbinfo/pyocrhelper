**What is pyocrhelper?**

Ocropus is a high quality OCR software which accepts images files as input and outputs html text files. Ocropus is quite good at what it does. pyocrhelper is a python class which makes interacting with Ocropus easier for an end user or a developer by taking care of all the steps which have to be taken before Ocropus can be used:

  1. determine filetype of input file
  1. if (etc) pdf, convert pdf to images
  1. convert input image(s) to Ocropus input image
  1. run Ocropus on the input image(s)
  1. format the Ocropus output (concatenating files if necessary)

**What features does pyocrhelper currently have?**

Right now, there is  a tarball release v0.1 available at http://code.google.com/p/pyocrhelper/downloads/list but the most usable stuff is probably in the development tree (you'll have to check out the source from SVN - see http://code.google.com/p/pyocrhelper/source/checkout for further details

Currently, the feature set of pyocrhelper includes (but might not be limited to):
  * recognition of input file formats
  * conversion of pdf to images
  * conversion of input file images to target file images (defaults to png)
  * connect to and use ocropus using python's subprocess
  * concatenate multiple results (e.g. in case of pdf) to single file
  * **use cluster analysis to determine average and above average line break**
  * stripping of unnecessary html tags/format from output when concatenating
  * convert html output to text if required

**What features are planned for the future?**

As the entirety of pyocrhelper was developed as a python class, it is conceivable that it could be included in any python script or (e.g.) pyQT4 application, such as in KDE. A KDE4 plasmoid would be quite cool as well, but I can't find any information on python for plasma. It'll probably be available when KDE4.1 comes out.

Apart from GUI interfaces, I want to build a proper conversion utility for html to OpenOffice/OpenDocument ODT format. There are some already available but I haven't been able to get any of them working...yet.

Another idea which might actually be useful is to build a utility to recursively scan an entire collection of (etc) PDFs to generate an index which can be stored in a database or searched etc. Once the class file is done properly and strengthened, it will be possible to develop around it.

As a final point, it is anticipated that as Ocropus develops, faster/better/more flexible utilities will grow out of it - this script should at least help to bridge the time until then.