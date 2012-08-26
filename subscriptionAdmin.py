import os
from parameterUtils import getConfigParameters
from instagram import InstagramAPI

#///////////////////////////////////////////////////////////////////////////////////////////////
#
# Set of example calls and examples to the instagram API to setup, review or delete subscriptions.
# 
#
#///////////////////////////////////////////////////////////////////////////////////////////////

cwd = os.getcwd()
cfgs = os.path.join(cwd, 'config/consumeIgram.cfgPrivate')
p = getConfigParameters(cfgs)

# Get the client and secret keys
api = InstagramAPI(client_id=p.client, client_secret=p.secret)

# Create a geographic subscription for San Francisco
api.create_subscription(object='geography', lat=37.7750, lng=-122.4183, radius=5000, aspect='media', callback_url=p.subBaseUrl)

#*** NOTE THAT p.subBaseUrl is in the consumeIgram.cfg config file - change this to whatever your realtime_callback url is ***

# Create a tag based subscription for olympics2012
#api.create_subscription(object='tag', object_id='olympics2012', aspect='media', callback_url=p.subBaseUrl)

# To see a list of your subscriptions, in the browser, hit...
#https://api.instagram.com/v1/subscriptions?client_secret=<yourSecret>&client_id=<yourClient>

# *** There is a way to programmatically hit this too, I just haven't bothered.

# To delete a subscription:
#x = api.delete_subscriptions(id=<get this ID number from looking at the active subscriptions listed - see lines above>)

