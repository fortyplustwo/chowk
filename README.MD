chowk
=====

chowk acts as a interface between RapidPro and any number of Kannel servers that you have by
passing messages to and fro in a format that both will understand.


Who and how does chowk help ?
----------------
If you have multiple Kannel servers and need to pass on each message originating from RapidPro
to the "right" kannel server based on the number series of the recipient (ie. the network operator),
chowk helps you.

Please note that chowk only helps in case of 1-to-N connections of Rapidpro and Kannel servers and *not* vice versa.

Currently it:
-------------

* Takes a message from RapidPro and sends it to the Kannel server based on the starting series of the recipient's phone number.
* Forward a message from any Kannel server to the RapidPro instance.
* Send a confirmation report to RapidPro, of the message being successfully handed over to a Kannel server.
* Send a delivery reprot to RapidPro, when a Kannel server informs of message being delivered.
* Send a failure report to RapidPro, of any failures reported by any Kannel server.


In future it will:
------------------
* Have better error messsages and email based reporting and file based logging of exceptions, errors and warnings.
* Support SSL in connections with RapidPro and Kannel.
* Use Greenlet/eventlets to make things beter, faster and easier (??)
* Authenticate requests from RapidPro and Kannel to ensure they are actually coming from where they say they are coming.

What's in the name?
--------------------

chowk is Hindi/Marathi/Indian vernacular slang for a traffic square where different routes meet and traffic is controlled and directed.
