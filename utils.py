from settings import KANNEL_SERVERS, DEFAULT_KANNEL_SERVER, ROOT_URL
from requests import Request, Session, post

def get_kannel_server(r):
    '''retrieves the ip of the origin of the given request and identifies the Kannel server'''
    #TODO: Test when chowk is behind nginx connection
    
    #according to http://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-python-flask, try accessing
    #any headers which may be put up by  a reverse proxy on our end and contain the actual ip address of the client

    if 'HTTP_X_FORWARDED_FOR' in r.environ:
        ip = r.environ['HTTP_X_FORWARDED_FOR']
    elif 'REMOTE_ADDR' in r.environ:
        ip = r.environ['REMOTE_ADDR']
    else:
        return False

    for k in KANNEL_SERVERS:
        if KANNEL_SERVERS[k]['host'] == ip:
            return k
        else:
            continue

    return False

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
