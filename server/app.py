from flask import Flask, request, jsonify
from flask_cors import CORS
import csv

app = Flask(__name__)

CORS(app)

@app.route('/sendData', methods=['POST'])
def submit_form():
    receivedData = request.json
    print(receivedData)  # You can process the data as needed

    if ('eventName' not in receivedData) or ('typeName' not in receivedData) or ('QRcode' not in receivedData): 
        return 'Data is missing', 400
    
    addingData = [receivedData['eventName'],receivedData['typeName'],receivedData['QRcode']]
    with open('dataSheet.csv','a',newline='') as file:
        writer = csv.writer(file)

        writer.writerow(addingData)

    return jsonify({"status": "success", "data_received": receivedData})

if __name__ == '__main__':
    app.run(debug=True)