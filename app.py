from flask import Flask, request, abort
from router import send_to_kannel
app = Flask(__name__)

@app.route("/")
def index():
        return "<h2>Welcome to chowk!</h2>"

@app.route("/sendsms/", methods = ['POST'])
def sendsms():
    if not request.method == 'POST':
        return "Wrong request. Get off my server you idiot and RTFM!"
    else:
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
                return "OK"
        except KeyError as e:
            print e
            print e.msg
            raise e
            return "Wrong request data. Get off my server you idiot and RTFM!"

if __name__ == "__main__":
       app.run(debug=True, host='0.0.0.0')
