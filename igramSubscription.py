import os
import json
import urllib2
#import jmsCode                      # JMS STOMP connection wrapper - needs stomp.py
import datetime

#///////////////////////////////////////////////////////////////////////////////////////////////
#
# Set of functions to handle the update payload from an instagram subscription update POST. 
#
# The main() seems a bit convoluted, but it handles the possibility of multiple updates in a 
# single POST. And then it handles each media item (photo) returned from the GET call the the
# relevant search endpoint.
# 
# It also handles the recording of the next URL, so that each call only gets the most recent
# content that has not been retrieved before. It does that by retrieving either a 'min_id' (in the
# case of the geography) or a 'next_url' (in the case of a tag) and storing this for the next time.
#
# The next URL (from geog and from tag) is stored in a text file named according to the object_id
# for the subscription in the /config directory. The code attempts to open this for every update
# and read the next url. If it can't, it just proceeds in getting all that is available.
#
# Media metadata is either put out over JMS (not tested yet) or dumped straight to a file as JSON.
#
# If on dotcloud, check /var/log/supervisor/uwsgi.log for any print outs/errors.
# Also, note that if deploying on dotcloud you will need a custom build to ensure nginx can 
# accept big enough POST payloads.
#
#
#///////////////////////////////////////////////////////////////////////////////////////////////

def getNextUrl(p, object_id):
    ''' See whether the url to use has already been written to a file '''
    
    outDir = os.path.dirname(p.configFile)
    if str(object_id) in os.listdir(outDir):
        f = open(os.path.join(outDir, str(object_id)), 'r')
        url = f.read()
        f.close()
    else:
        url = None
        
    return url

#------------------------------------------------------------------------------------------------

def formatMetadata(mediaMeta):
    ''' Retrieves those fields that would usefully be stored in the same format as twitter do it.
        This allows downstream processors to (hopefully) handle the data irrespective of source.
        It stores the original too, but duplicates fields containing time/geo/hashtags/text. '''

    # Get the data list
    eventsIn  = mediaMeta['data']
    eventsOut = []
    
    for data in eventsIn:

        # Assign caption text to the 'text' field
        try:
            data['text'] = data['caption']['text']
        except:
            data['text'] = None
            
        # Assign the created_time to created_at
        dt = datetime.datetime.fromtimestamp(float(data['created_time']))
        data['created_at'] = dt.strftime('%a %b %d %H:%M:%S +0000 %Y')
        
        # Deal with entities/tags - put each of the tags into the hashtag structure
        entities = {"urls": [],"hashtags": [],"user_mentions": []}
       
        # Loop the tags on the photo, add them to an 'entities' dict
        for tag in data['tags']:
            try:
                entities['hashtags'].append({'text':str(tag), 'indices':[]})
            except:
                pass
        
        # Add that entities dict to the original data
        data['entities'] = entities
    
        # Deal with geolocation information
        try:
            lat = float(data['location']['latitude'])
            lon = float(data['location']['longitude'])
        except:
            lat, lon = None, None
        
        # Note the switcheroo of the lat/lon between these 2 sets
        data["geo"]         = {"type": "Point", "coordinates": [lat, lon]}
        data["coordinates"] = {"type": "Point", "coordinates": [lon, lat]}
        
        eventsOut.append(data)
    
    # Return the original photo metadata with some fields added (duplicated)
    # to ensure they're in the twitter format
    return eventsOut

#------------------------------------------------------------------------------------------------

def getMediaUpdates(url):
    ''' Reads and parses the subscription updates'''
  
    try:
        response = urllib2.urlopen(url)
        mediaMeta = json.loads(response.read())
    except:
        mediaMeta = None
        print "Failed to open this url: \n %s" %url
        
    return mediaMeta 

#------------------------------------------------------------------------------------------------

def handleMediaPagination(p, url, object_id, mediaMeta):
    ''' Extracts the pagination information relating to the next set of update data'''

    nextUrl = None
    
    # See if there is a pagincation key in the media metadata
    if mediaMeta and mediaMeta.has_key('pagination'):
        pagination = mediaMeta['pagination']
        
        # If it has a next_url, then get that for the next time this gets updated - they tell you what its going to be
        if pagination.has_key('next_url') and pagination['next_url'] != None:
            nextUrl = pagination['next_url']
        
        # Geography subscriptions, just have a next_min_id, which is used to get the next data. 
        elif pagination.has_key('next_min_id') and pagination['next_min_id'] != None:
            minId = pagination['next_min_id']
            
            # Strip out the base url. Catch the first instance where it shouldn't have an & in it
            amp = url.find('&')
            if amp != -1:
                url = url[:amp+1]
            nextUrl = "%s&min_id=%s" %(url, minId)
            
        else:
            pass
            
    else:
        print "Failed too retrieve either mediaMeta or the pagination key."
        
    # Where we've been successful getting the next url, dump it out to a file for next time
    if nextUrl:
        try:
            outDir = os.path.dirname(p.configFile)
            outName = os.path.join(outDir, str(object_id))
            fOut = open(outName, 'w')
            fOut.write(nextUrl)
            fOut.close()
        except:
            print "Failed to write out next URL for object_id : %s \n %s" %(object_id, nextUrl)
    
    return

#------------------------------------------------------------------------------------------------

def buildUrl(p, obj, objectId):
    ''' Submits the request to the SEARCH api for the actual media update.
        This gets called if the pagination function doesn't get used.
        The pagination function gets the 'next' url from the current message,
        That url ensures you don't get dupes.'''
    
    # Swap out the geography id
    if obj == 'geography':
        url = p.geoUrl.replace('<geo-id>', str(objectId))

    # Swap out the tag
    if obj == 'tag':
        url = p.tagUrl.replace('<tag>', str(objectId))
        
    # Sub out the client id for authorisation
    url = url.replace('<client-id>', str(p.client))
    
    return url

#------------------------------------------------------------------------------------------------


def main(p, response):
    '''Handles the subscription updates, including making the call to the endpoint and dumping to jms/text.'''

    # Make the JMS connection via STOMP and the jmsCode class    
    if p.jmsBase == True:
        import jmsCode
        jms = jmsCode.jmsHandler(p.jmsHost, p.jmsPort, verbose=True)
        jms.connect()
    
    # If the config says save it out to file, do so
    if p.fileBase == True:
        outDir = os.path.dirname(p.configFile)

    # Accepts a list of dictionaries - the update message
    updates = json.loads(response)

    # Format the url and get the media metadata
    for upd in updates:
                
        # Does the next URL already exist for this object?
        url = getNextUrl(p, upd['object_id'])
        
        # If the next (ie this) url hasn't been written to a file, build it from the config file 
        if url == None:
            url = buildUrl(p, upd['object'], upd['object_id'])
        
        # Get the media that has changed since the last time
        mediaMeta = getMediaUpdates(url)    
        
        # Find the pagination info and save out info that concerning next url for this subscription
        handleMediaPagination(p, url, upd['object_id'], mediaMeta)
                
        # Format the content - make it like a tweet
        data = formatMetadata(mediaMeta)
        
        # Loop each photo that is referenced by this update and either save it out or message it
        for photo in data:
            
            # Dump the media metadata out to a string
            jPhoto = json.dumps(photo, ensure_ascii=True)

            # Write the json for this photo out to file            
            if p.fileBase == True:
                f = open(os.path.join(outDir, str(photo['id'])+'.json'), 'w')
                f.write(jPhoto)
                f.close()
            
            # Put the metadata onto the JMS
            if p.jmsBase == True:
                jms.sendData(p.jmsDest, jPhoto, photo['id'])
    
    # Close the jms connection
    if p.jmsBase == True:
        jms.disConnect()
        