from settings import KANNEL_SERVERS

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
