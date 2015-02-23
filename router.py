from requests import Request, Session, post
from settings import KANNEL_SERVERS, DEFAULT_KANNEL_SERVER, RAPIDPRO_URLS, ROOT_URL

def compose_request_for_kannel(msg = {}, server = DEFAULT_KANNEL_SERVER):
    '''composes a proper Request using the given msg and kannel server details'''

    params = {  #the data to be sent as query string with the URL
            'username' : server['username'],
            'password' : server['password'],
            'from'     : msg['from'],
            'to'       : msg['to'],
            'text'     : msg['text'],
            'smsc'     : server['smsc'],
    }

    #also ask for delivery reports
    #ref: http://www.kannel.org/download/1.4.0/userguide-1.4.0/userguide.html#DELIVERY-REPORTS
    if server['smsc'] is not None: #since SMSC IDs are *required* for getting delivery reports,
        params['dlr-mask'] = 31 #31 means we get ALL Kind of delivery reports.
        params['dlr-url'] = ROOT_URL + "/deliveredsms/?msgid=%s&dlr-report-code=%%d&dlr-report-value=%%A" % msg['id']


    url = "http://%s:%s/%s" % (server['host'],server['port'],server['path']);
    
    #return a prepared Request
    r = Request('GET', url, params = params)
    return r

def send_to_rapidpro(app, msg = {}):
    '''sends a given message to the RapidPro server'''

    try:
        #if there is a keyword in the message, just remove it before forwarding to RapidPro
        keyword = KANNEL_SERVERS[msg['host']]['keyword']
        app.logger.debug("The server %s use the keyword %s", msg['host'], keyword)

        if keyword is not None:
            text = msg['text'].split()
            if text[0].upper() == keyword.upper(): #match using the same case
                app.logger.debug("Removing keyword %s from the message %s", keyword, msg['text'])
                msg['text'] = " ".join(text[1:]) #remove the keyword from the message and reconstruct the SMS

        url = RAPIDPRO_URLS['RECEIVED']

        data = { #the data to be sent in the body of the request
                'from'  : msg['from'],
                'text'  : msg['text'],
        }
        r = post(url=url, data = data)
        app.logger.debug("Sending request to RapidPro server at %s", r.url)
        app.logger.debug("Data inside request to RapidPro server is %s", r.request.body)
        app.logger.debug("The response we got from RapidPro is %s", r.text)

        r.raise_for_status() #Will raise an exception with the HTTP code ONLY IF the HTTP status was NOT 200
        return True
    except Exception as e:
        app.logger.debug("Exception %s occurred", e)
        raise e

def send_to_kannel(app, msg = {}, preferred_kannel_server = None):
    '''sends a given messages to the _RIGHT_ kannel server'''
    server = None
    if preferred_kannel_server is not None:
        try:
            server = KANNEL_SERVERS[preferred_kannel_server.lower()] #locate using ip
        except KeyError as ke:
            server = KANNEL_SERVERS['DEFAULT_KANNEL_SERVER']
    else: #no preferred server was given, select the proper one based on the recipient number
    
        for s,s_info in KANNEL_SERVERS.items():
            prefixes = s_info['series']
            app.logger.debug("Server %s supports all numbers with the prefixes %s", s, prefixes)
            for p in prefixes:
                recipient = msg['to'].strip('+')
                app.logger.debug("Trying to match %s with prefix %s ", recipient, p)
                if recipient.startswith(p): #this is our number series
                    server = s_info 
                    app.logger.debug("Selected server %s with prefix (%s) matching with recipient number %s", server, prefixes,recipient)
                    break;

            if server is not None: #we have found our server!
                break;


    if server is None:
        app.logger.error("Could not select any server for forwarding message! Check logs.")
        return False

    #compose the complete Request with URL and data for sending sms
    session = Session()

    request = session.prepare_request(compose_request_for_kannel(msg, server))
    app.logger.debug("Calling %s with data %s", request.url, request.body)
    response = session.send(request)

    print response.status_code
    print response.text
    app.logger.debug("Received response code %s with text %s", response.status_code, response.text)

    return (True, response.status_code, response.text)
    #call it.

def report_status_to_rapidpro(status, msg, app):
    '''Reports a specific delivery STATUS info about the msg to RapidPro
       This includes:
       1. SENT (A SMS has been given to the SMSC for delivering to the PHONE)
       2. DELIVERED (A SMS has been delivered to the PHONE)
       3. FAILURE (A SMS failed delivery because of problems at the SMSC end OR at the PHONE)

       There is currently no clear distincition required by the RapidPro for the 3rd type of status
       and hence, we don't make it.
    '''
    app.logger.debug("Status is %s", status)
    #TODO
    #FAILURE should be reported when 
    #1. When Kannel reports a deliver failure, by calling chowk's dlr-url route 
    #2. When an unrecoverable exception occurs when we are trying to handover a msg to Kannel for delivery
    try:
        if status is None: #THERE is NO status to report!
            raise Exception("Status was not specified!")
        elif status.upper() == 'SENT':
            url = RAPIDPRO_URLS['SENT']
        elif status.upper() == 'DELIVERED':
            url = RAPIDPRO_URLS['DELIVERED']
        elif status.upper() == 'FAILED':
            url = RAPIDPRO_URLS['FAILED']

        data = {
                'id' : msg['id'],
        }

        #Send a POST request to RapidPro server informing that the message has been queued successfull for sending at Kannel
        r = post(url = url, data = data)
        app.logger.debug("Informed RapidPro at %s that delivery status of msgid %s at Kannel server is %s", r.url,r.request.body, status)
        app.logger.debug("The RapidPro server replied %s", r.text)
        return True
    except Exception as e:
        app.logger.debug("Exception %s occurred", e)
        raise e
        return False


