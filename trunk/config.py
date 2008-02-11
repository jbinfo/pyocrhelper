import os
from ConfigParser import SafeConfigParser
class Configuration:
    def __init__ (self, fileName):
        cp = SafeConfigParser()
        cp.read(fileName)
        self.__parser = cp
        self.fileName = fileName

    def __getattr__ (self, name):
        if name in self.__parser.sections():
            return Section(name, self.__parser)
        else:
            return None

    def __str__ (self):
        p = self.__parser
        result = []
        result.append('<Configuration from %s>' % self.fileName)
        for s in p.sections():
            result.append('[%s]' % s)
            for o in p.options(s):
                result.append('%s=%s' % (o, p.get(s, o)))
        return '\n'.join(result)

class Section:
    def __init__ (self, name, parser):
        self.name = name
        self.__parser = parser
    def __getattr__ (self, name):
        return self.__parser.get(self.name, name)

class Start:
    """
    Read the default configuration from file
    """
    def __init__(self,configfile='default'):
        if configfile == "default":
            #default_config = os.path.join(os.environ['HOME'],'.pyOcrHelper/pyOcrHelper.ini')
            default_config = os.path.join(os.getcwd(),"pyocrhelper.ini")
            if os.path.isfile(default_config):
                if not os.access(default_config,os.R_OK):
                    print "No permission to read %s"%default_config
                    exit()
                else:
                    file_to_use = default_config
            else:
                print "%s does not exist"%default_config
                exit()
        else:
            if not os.path.isfile(configfile):
                print "%s does not exist"%configfile
            else:
                if not os.access(configfile,os.R_OK):
                    print "No permission to read %s"%configfile
                else:
                    file_to_use = configfile
        try:
            config = Configuration(file_to_use)
        except Exception,e:
            print e
            exit()
        else:
            self.tmpdir  = config.Config.tmpdir
            self.outputFileFormat = config.Config.outputFileFormat
            self.ocrInputFormat = config.Config.ocrInputFormat
            self.ocrLocation = config.Config.ocrLocation
