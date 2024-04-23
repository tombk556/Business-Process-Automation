from website import create_app

app = create_app()

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(port=4000, debug=True)