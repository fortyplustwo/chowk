from flask import Flask, request, abort
from router import send_to_kannel, report_status_to_rapidpro, send_to_rapidpro
from utils import get_kannel_server
app = Flask(__name__)

@app.route("/")
def index():
        return "<h2>Welcome to chowk!</h2>"

@app.route("/sendsms/", methods = ['POST'])
def sendsms():
    '''Handles and processes all messages coming from RapidPro server and going towards Kannel servers'''
    try:
        #TODO: Validate data and sanitize it a bit (?? sanitizing necessary ??)

        #Collect data in the msg
        msg = {}
        msg['to'] = request.form['to']
        msg['channel'] = request.form['channel']
        msg['from'] = request.form['from']
        msg['text'] = request.form['text']
        msg['id'] = request.form['id']

        #construct and send it forward
        status = send_to_kannel(msg = msg, app = app)

        if status is False:
            return "Bad luck! Couldn't deliver your message. Try again later in 30 minutes."
            abort(500)
        else:
            #report back to the RapidPro server about the success of delivery of this message
            app.logger.debug("Message %s succesfully forwarded to Kannel server", msg)
            report_sent_to_rapidpro(msg = msg, app = app)
            #we return in the format (response, status, headers) so that RapidPro knows that everything is HTTP 200 :)
            return ('',200,[])
    except KeyError as e:
        print e
        print e.msg
        raise e
        return "Wrong request data. Get off my server you idiot and RTFM!"

@app.route("/receivesms/", methods = ['GET'])
def receivesms():
    '''Handles and processes all messages coming from Kannel and going towards the RapidPro server

       NOTE: See the enclosed sample configuration file in kannel/ for knowing what data is expected from Kannel
       and the name of the arguments
    '''
    try: #TODO: Better exception handling!
        app.logger.debug("Received data %s", request.args)
        #TODO: Support GET as well as POST requests equally well

        msg = {}
        msg['from'] = request.args['from']
        msg['text'] = request.args['text']
        msg['args'] = request.args

        #get the ip address of the kannel server so that we can identify it and using all the special info about i#t
        #if request.remote_addr
        msg['host']   = get_kannel_server(request)

        app.logger.debug("Identified! This message came from %s Kannel server", msg['host'])

        if msg['host'] is False: #if we can't get the IP of the origin of request, just abort the whole process
            raise Exception("Cannot retrieve IP from the request to recognize the Kannel Server. Aborting processing!")

        send_to_rapidpro(app = app, msg = msg)
        #we will NOT return any text because whatever is returned will be sent as SMS to the original sender by Kannel
        #we return in the format (response, status, headers) so that Kannel knows that everything is HTTP 200 :)
        return ('',200,[])

    except Exception as e:
        #TODO: Send an email when unrecoverable exceptions occur, instead of just logging to the file here!
        app.logger.debug("Exception %s occurred", e)
        raise e

@app.route("/deliveredsms/", methods = ['GET','POST'])
def deliveredsms():
    ''' Handles and processes any kind of delivery reports sent by Kannel servers '''

    app.logger.debug("Method used is %s", request.method)
    app.logger.debug("Delivery report is for msg id %s", request.form['id'])
    app.logger.debug("Delivery report is for msg id %s", request.args['id'])
    import pdb
    pdb.set_trace()

    #This will in turn use the report_delivered_to_rapidpro AND report_failed_to_rapidpro methods from router module.
    return "Not implemented!"

if __name__ == "__main__":
       app.run(debug = True, host = '0.0.0.0')
       from logging import FileHandler,DEBUG
       file_handler = FileHandler('./loggedfile.log')
       file_handler.setLevel(DEBUG)
       app.logger.addHandler(file_handler)
