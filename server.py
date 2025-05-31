from flask import Flask, request, jsonify, send_from_directory
from dataservices import dataservices

# Flask app
app = Flask(__name__, static_folder="static")

# Serve index.html
@app.route("/", methods=["GET"])
def index():
	return send_from_directory("static", "index.html")


@app.route("/data/catalogue", methods=["GET"])
def catalogue():
	return dataservices.catalogue()


@app.route("/data/sales-prediction", defaults={'productId': None}, methods=["GET"])
@app.route("/data/sales-prediction/<productId>", methods=["GET"])
def predict(productId):
    return dataservices.salesPrediction(productId)


@app.route("/data/sentiments", methods=["GET"])
def sentiment():
	return dataservices.sentiments()


@app.route("/data/keywords", methods=["GET"])
def keywords():
	return dataservices.keywords()


@app.route("/data/opportunities", methods=["GET"])
def opportunities():
	return dataservices.opportunities()


if __name__ == "__main__":
	app.run(port=5000, debug=True)

