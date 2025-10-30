from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def root():

    return jsonify({'message':'This is the root page.'})



if __name__ == '__main__':
    
    app.run(debug=True)