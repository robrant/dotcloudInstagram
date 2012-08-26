The instagram bits
------------------
* This set of scripts and bottle app retrieves media metada based on the instagram real time subscriptions. It has a web app script (igram_app.py) that
does all the web stuff (subscription authentication, POST payload receipt) a set of handler functions (igramSubscription.py) that handles the update
payload and then makes calls to the relevant API endpoint to retrieve media metadata. It also then handles the media metadata and either puts it
onto a JMS (not possible with dotcloud) or writes it out to a file.

* For the JMS you will need stomp.py and a module with this call jmsCode.py

* One other class handles the configuration information so that its nicely tied up in a single object. (parameterUtils.py)

* And a final script/how to helps with the building, review and deletion of subscriptions (subscriptionAdmin.py)


dotcloud instagram custom service
---------------------------------

This is a beta version of the custom python service on dotCloud. It was modified an original custom service called python-on-dotcloud, available on github.

Why use this service
--------------------
From the original: "The most requested feature is the ability to change the uwsgi configuration. If you want to do that you just need to change the uwsgi.sh file."

So, thats what this is - a cloned copy with modifications to see whether POST buffering changes would allow me to accept incoming POSTs.

# Additional parameters to put into the uwsgi config on start up 
--pep333-input --post-buffering 4096 

Changes:
--------
1. Remove all newRelic references (here for info on newRelic: http://newrelic.com)
2. Leave postinstall well alone
3. Add in my requirements into requirements.txt
4. Change version number to 2.6 in dotcloud.yml
6. Added a static directory - NEED TO ADD TEMPLATES FOR THE RESPONSES IN SLOW TIME
7. Added the following lines to uwsgi.sh in the uwsgi call:
--pep333-input --post-buffering 4096 
8. THINK ABOUT TIDYING UP WITH A WEB DIRECTORY
9. Modified the wsgi to direct towards default app


Python Version
--------------
This custom service supports 4 different branches of python (2.6, 2.7, 3.1, 3.2), it will default to python 2.6 unless you specify otherwise. The current versions of each python branch are listed in the table below. Pick the branch that works best for you.

+--------+---------+
| branch | version |
+========+=========+
| 2.6*   | 2.6.5   |
+--------+---------+
| 2.7    | 2.7.2   |
+--------+---------+
| 3.1    | 3.1.2   |
+--------+---------+
| 3.2    | 3.2.2   |
+--------+---------+

\* python 2.6 is the default

Here is an example of the dotcloud.yml file for setting the python version to 3.2::

    python:
        type: custom
        buildscript: builder
        systempackages:
            # needed for the Nginx rewrite module
            - libpcre3-dev
        ports:
            www: http
        processes:
            nginx: nginx
            uwsgi: ~/uwsgi.sh
        config:
            python_version: 3.2
