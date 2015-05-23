**pyocrhelper v0.1**

---





**ABOUT**

---

Ocropus is a high quality OCR software which accepts images files as input and
outputs html text files. Ocropus is quite good at what it does. pyOcrHelper is
a python class which makes interacting with Ocropus easier for an end user or
a developer by taking care of all the steps which have to be taken before
Ocropus can be used:

  1. determine filetype of input file
  1. if (etc) pdf, convert pdf to images
  1. convert input image(s) to Ocropus input image
  1. run Ocropus on the input image(s)
  1. format the Ocropus output (concatenating files if necessary)

You can checkout the pyocrhelper source from Google SVN with the following
command:
svn checkout http://pyocrhelper.googlecode.com/svn/trunk/ pyocrhelper-read-only

There may also be releases available at:
http://code.google.com/p/pyocrhelper/downloads/list

There may also be an rpm available at:
https://build.opensuse.org/project/show?project=home:babelworx
http://software.opensuse.org/search?q=pyocrhelper




**USEFUL HINTS ON OBTAINING AND INSTALLING OCROPUS**

---

Ocropus is available directly from the ocropus google code project at http://code.google.com/p/ocropus - if you want to configure and build it yourself, that is. A much better and easier solution is to use the [openSUSE build service](http://build.opensuse.org). Ocropus and tesseract are both packaged there for openSUSE and for some other distributions as well. Here are the download links:

Ocropus: http://software.opensuse.org/search?baseproject=ALL&p=1&q=ocropus
Tesseract: http://software.opensuse.org/search?baseproject=ALL&p=1&q=tesseract

In both cases use the binaries from home:jnweiger