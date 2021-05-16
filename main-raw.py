from flask import Flask, render_template, request, jsonify
import aiml
import os
import mnbpy
import logpy
import pickle
import pandas as pd
import csv

mnb = pickle.load(open('mnb.pickle', 'rb'))
log = pickle.load(open('log.pickle', 'rb'))

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])
def ask():

    message =request.form['messageText'].strip()

    kernel = aiml.Kernel()

    if os.path.isfile("bot_brain.brn"):
        kernel.bootstrap(brainFile = "bot_brain.brn")
    else:
        kernel.bootstrap(learnFiles = os.path.abspath("aiml/startup.xml"), commands = "load aiml b")
        kernel.saveBrain("bot_brain.brn")

    while True:
        if message == "quit":
            exit()
        elif message == "save":
            kernel.saveBrain("bot_brain.brn")
        else:
            bot_response = kernel.respond(message)
            if (bot_response == "NULL"):

                testa=mnbpy.clean_text(message)
                if(len(testa.split())>1):

                    X_test=pd.Series(testa)
                    y_prednb = mnb.predict(X_test)
                    y_predlog = log.predict(X_test)

                    if(y_prednb==y_predlog):
                        csv_f = csv.reader(open('answers.csv',encoding='utf-8'))

                        for row in csv_f:
                            if(row[0]==str(y_prednb[0])):
                                gt=row[1]
                                print (row[1])

                    else:
                        gt="Please provide more information"
                else:
                    gt="Please provide more information"

                return jsonify({'status':'OK','answer':'$'+gt})


            else:
                return jsonify({'status':'OK','answer':bot_response})


if __name__ == "__main__":
    app.run(host='localhost', debug=True)
