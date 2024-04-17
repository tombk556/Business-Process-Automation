from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    hallo = "hallo"
    print(hallo)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
