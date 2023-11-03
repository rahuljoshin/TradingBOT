from flask import Flask
from iBullsbearsAlgo import start
app = Flask(__name__)

@app.route('/')
def startiBuulsBearsBot():
    start()

if __name__ == '__main__':
    app.run()