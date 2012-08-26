import os
import bottle
from bottle import route, post, run, request, static_file
#from instagram import client, subscriptions
import igramSubscription
from parameterUtils import getConfigParameters

bottle.debug(True)

#///////////////////////////////////////////////////////////////////////////////////////////////
#
# Bottle (python micro-framework) based web application for interacting with the instagram API.
# 
# A web server is needed for instagrams pubsubhubub - based API. It is needed for the setting up
# of subscriptions (this app responds to say that the subscription is authorised). It is also 
# needed to receive update POSTs from the Instgram Publisher. The updates are small json payloads
# that notify this app that something matching the subscription has changed. The updates do not
# contain the media or the media metadata. 
#
# This app, upon receipt of an update POST, passes the payload to igramSubscrption(.py) which
# reads the update and hits the relevant API search endpoint to retrieve the recently changed
# media metadata.
#
# This app doesn't include any calls for authorising other applications or users. It just handles
# the updates and subscription authorisation. An update payload looks like this:-
#
# [{"changed_aspect": "media", "subscription_id": 2229309, "object": "tag", "object_id": "olympics2012", "time": 1345065662}]
# 
# Note, its a list so you have multiple updates in a single payload - the code is written to handle that.
#
#
#///////////////////////////////////////////////////////////////////////////////////////////////

os.chdir('/home/dotcloud/current/')
cwd = os.getcwd()
cfgs = os.path.join(cwd, 'config/consumeIgram.cfg')
p = getConfigParameters(cfgs)

#------------------------------------------------------------------------------------------------

def on_error(errFile='errors.txt', message=None):
    ''' Handles an error message '''
    
    f = open(os.path.join(cwd, errFile), 'a')
    f.write(message + '\n')
    f.close()

#------------------------------------------------------------------------------------------------

@route('/realtime_callback')
@post('/realtime_callback')
def on_realtime_callback():
    ''' The function that does both the subscription authorisatin - a response to their server
        and receives the POST payload to get the update messages for building endpoint fetches'''
    
    # Challenge to be responded to - this allows subscriptions to be setup
    challenge = request.GET.get("hub.challenge")
    if challenge: 
        return challenge

    # If its a POST, get the payload
    try:
        raw_response = request.body.read()
    except:
        on_error(message='Failed on body read request.')
    
    # Make sure that the payload exists
    if raw_response == None:
        on_error(message='Failed on body read request.')
    else:
        igramSubscription.main(p, raw_response)

#------------------------------------------------------------------------------------------------

@route('/test')
def test():
    ''' General GET test to see whether there are errors in this file '''
    f = open(os.path.join(cwd, 'test.txt'), 'a')
    f.write('writing out the test line from hitting this site.')
    f.close()
    return "Hello world - this worked"

#------------------------------------------------------------------------------------------------

@route('/subscription_response')
def on_subscription_request():
    ''' Not needed - superseeded by realtime_callback() '''
    code = request.GET.get("hub.challenge")
    if not code:
        return 'Missing code'
    else:
        return code
