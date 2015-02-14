from requests import Request, Session
from settings import KANNEL_SERVERS, DEFAULT_KANNEL_SERVER

def compose_request(msg = {}, server = DEFAULT_KANNEL_SERVER):
    '''composes a proper Request using the given msg and kannel server details'''
    data = {
            'username' : server['username'],
            'password' : server['password'],
            'from'     : msg['from'],
            'to'       : msg['to'],
            'text'     : msg['text'],
    }

    url = "http://%s:%d/%s" % (server['host'],server['port'],server['path']);
    
    #return a prepared Request
    app.logger
    r = Request('GET', url, data = data).prepare()
    return r

def send_to_kannel(app, msg = {}, preferred_kannel_server = None):
    '''sends a given messages to the _RIGHT_ kannel server'''
    server = None
    if preferred_kannel_server is not None:
        try:
            server = KANNEL_SERVERS[preferred_kannel_server.lower()] #locate using ip
        except KeyError as ke:
            server = KANNEL_SERVERS['DEFAULT_KANNEL_SERVER']
    else: #no preferred server was given, select the proper one based on the recipient number
    
        for s in KANNEL_SERVERS:
            prefixes = s['series']
            for p in prefixes:
                recipient = msg['from'].strip('+') 
                if recipient.startswith(p): #this is our number series
                    server = s 
                    app.logger.notice("Selected server %s with prefix (%s) matching with recipient number %s", (server, prefixes,p))
                    break;

            if server is not None: #we have found our server!
                break;


    if server is None:
        app.logger.error("Could not select any server for forwarding message! Check logs.")
    return False

    #compose the complete Request with URL and data for sending sms
    session = Session()

    request = compose_request(msg, server)
    app.logger.notice("Calling %s with data %s", (request.url, request.body))
    response = session.send(request)

    print response.status_code
    print response.text
    app.logger.info("Received response code %s with text %s", (response.status_code, response.text))

    return True
    #call it.

