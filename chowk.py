from flask import Flask, request, abort
from tasks import send_to_kannel, report_status_to_rapidpro, send_to_rapidpro, testtask
from utils import get_kannel_server
import traceback
import sys
import logging

#
app = Flask(__name__)

#define a file-based logger
#TODO: Have a Email-based logger for ERROR and CRITICAL, while a RotatingFileLogger for WARNING and below
from logging import DEBUG,ERROR
rfh = logging.handlers.RotatingFileHandler('./chowk.log')
rfh.setLevel(DEBUG)

efh = logging.handlers.RotatingFileHandler('./error.log')
efh.setLevel(ERROR)

#Now, add handlers to all loggers
loggers = [app.logger, logging.getLogger('tasks')]

for l in loggers:
    l.addHandler(rfh)
    l.addHandler(efh)

#Make this logger available to any functions outside this module

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

        app.logger.debug("We got request form data in the body as", request.form)
    
        #construct and send it forward
        r = send_to_kannel.apply_async(kwargs = {'msg': msg}, serializer = 'json')
        r.wait()
        status, status_code, status_msg = r.result
        exc_info = sys.exc_info()

        #We now try to find out the cause for failures, if any.
        #TODO: Handle this using and raising exceptions in send_to_kannel instead of anything else.

        if status_code == 403: #AuthenticationError with the Kannel
            app.logger.critical("Internal authentication error when trying to send the message to %s! Check config!", msg['to'])
            app.logger.critical("MSG Details are %s", msg)
            abort(500)
        elif status != False or status_code != 200:
            return "Bad luck! Couldn't deliver your message. Try again later in 30 minutes."
            abort(500)
        else:
            #report back to the RapidPro server about the success of delivery of this message
            app.logger.debug("Message %s succesfully forwarded to Kannel server", msg)
            report_status_to_rapidpro.apply_async(kwargs = {'status': 'SENT', 'msg': msg}, serializer = 'json')
            #we return in the format (response, status, headers) so that RapidPro knows that everything is HTTP 200 :)
            return ('',200,[])
    except KeyError as ke:
        exc_info = sys.exc_info()
        print "KeyError", ke
        app.logger.exception(ke)
        raise ke
        return "Wrong request data. Get off my server you idiot and RTFM!"
    except Exception as e:
        exc_info = sys.exc_info()
        print "Exception ", e
        app.logger.exception(e)
        raise e
        return "Error occured while trying to process your request"
    finally:
        traceback.print_exception(*exc_info)
        del exc_info


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

        send_to_rapidpro.apply_async(kwargs = {'msg': msg}, serializer = 'json')
        #we will NOT return any text because whatever is returned will be sent as SMS to the original sender by Kannel
        #we return in the format (response, status, headers) so that Kannel knows that everything is HTTP 200 :)
        return ('',200,[])

    except Exception as e:
        #TODO: Send an email when unrecoverable exceptions occur, instead of just logging to the file here!
        app.logger.debug("Exception %s occurred", e)
        raise e

@app.route("/deliveredsms/", methods = ['GET'])
def deliveredsms():
    ''' Handles and processes any kind of delivery reports sent by Kannel servers '''

    #This will in turn use the report_delivered_to_rapidpro AND report_failed_to_rapidpro methods from router module.

    try:
        msg = {}
        msg['id'] = request.args['msgid']
        msg['dlr-report-code'] = int(request.args['dlr-report-code'])
        msg['dlr-report-value'] = request.args['dlr-report-value']
        app.logger.debug("Delivery report is for msg id %s with code %s and text %s", msg['id'], msg['dlr-report-code'], msg['dlr-report-value'])

        #based on the dlr_code, determine which method to call for reporting back to RapidPro server
        #Uses a composite OF 
        #1.http://kannel.org/download/1.4.4/userguide-1.4.4/userguide.html#delivery-reports
        #2.http://kannel.org/download/1.4.4/userguide-1.4.4/userguide.html#AEN5058

        if msg['dlr-report-code'] == 1: #delivery success in delivering to PHONE
            report_status_to_rapidpro.apply_async(kwargs = {'status': 'DELIVERED', 'msg': msg}, serializer = 'json')
        elif msg['dlr-report-code'] == 8: #delivery success in delivering to the SMSC
            report_status_to_rapidpro.apply_async(kwargs = {'status': 'SENT', 'msg': msg}, serializer = 'json')
        elif msg['dlr-report-code'] == 2: #delivery FAILURE in delivering to PHONE
            report_status_to_rapidpro.apply_async(kwargs = {'status': 'FAILED', 'msg': msg}, serializer = 'json')
        elif msg['dlr-report-code'] == 16: #delivery FAILURE in delivering to SMSC; most probably a rejection by SMSC
            report_status_to_rapidpro.apply_async(kwargs = {'status': 'FAILED', 'msg': msg}, serializer = 'json')
        elif msg['dlr-report-code'] == 4: #QUEUED on the bearerbox of Kannel for delivery in future
            #TODO: Do something better than just ignoring this status!
            pass;
        elif msg['dlr-report-code'] == 32: #Intermediate notifications ??
            #TODO: Find out what all possible dlr-report-values are sent at such time.
            pass

        return ('',200,[]) #return HTTP 200 without any text inside

    except Exception as e:
        #TODO Send an email report with all the request.args so on
        app.logger.exception(e)
        raise e
        abort(500)

if __name__ == "__main__":
       app.run(debug = True, host = '0.0.0.0')
       app.logger.debug("Starting debugging")
