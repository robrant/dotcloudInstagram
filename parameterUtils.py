import ConfigParser
import json

# Just gets the config parameters into an object for ease of handling in the code.
# Almost definitely a better way of doing this...?

class getConfigParameters():
    ''' Gets the configuration parameters into an object '''
    
    def __init__(self, filePath):
        
        config = ConfigParser.ConfigParser()
        try:
            config.read(filePath)
        except Exception, e:
            print "Failed to read the config file for instagram subscriptions."
            print e
        
        # Keep the location of the config file in the config file for mods on the fly
        self.configFile = filePath
            
        # Default parameters
        self.dataSource = config.get('default', 'dataSource')
        self.verbose = config.getboolean('default', 'verbose')
    
        # Source parameters
        self.client      = config.get("source", "client")
        self.secret      = config.get("source", "secret")
        
        # These are the starting point URLs for getting the data - they get modified in the code
        self.geoUrl      = config.get("source", "geoUrl")
        self.tagUrl      = config.get("source", "tagUrl")
        self.subBaseUrl  = config.get("source","subBaseUrl")
        
        # JMS parameters - whether its AMQP or STOMP
        self.jmsHost = config.get("messageBroker",        "jmsHost")
        self.jmsPort = config.getint("messageBroker",     "jmsPort")
        self.jmsDest = config.get("messageBroker",        "jmsDest")
        self.jmsBase = config.getboolean("messageBroker", "jmsBase")
        self.fileBase= config.getboolean("messageBroker", "fileBase")

#------------------------------------------------------------------------------------------ 


