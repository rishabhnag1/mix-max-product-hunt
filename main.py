from flask import Flask, request, json, abort, render_template
from flask_cors import CORS
from bs4 import BeautifulSoup
import logging
import requests
app = Flask(__name__)
cors = CORS(app, origins="/^[^.\s]+\.mixmax\.com$/", support_credentials=True)

@app.route("/resolver")
def product_hunt_resolver():
    url = request.args.get("url")
    user = request.args.get("user")

    if url is None or user is None:
        log.info("Invalid request params for URL and/or user {}".format(url, user))
        return abort(400)

    log.info("Received request for URL {} from user {}".format(url, user))

    body, subject = get_url_summary(url)
    if body is None or subject is None:
        log.info("Aborting request, unable to retrieve summary")
        return abort(400)

    resp_data = dict([("body", body), ("subject", subject)])
    resp = app.response_class(
        response=json.dumps(resp_data),
        status=200,
        mimetype="application/json"
    )

    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Origin"] = "https://compose.mixmax.com"
    log.info("Completed request for URL {} from user {}".format(url, user))
    return resp


def get_url_summary(url):
    if "http://" not in url and "https://" not in url:
        url = "http://" + url
    resp = requests.get(url)
    if not resp.ok:
        return (None, None)

    if resp.content is None:
        return (None, None)

    html = BeautifulSoup(resp.text, "html.parser")
    subject = html.title.string
    body = render_template("/index.html", url=url, content=subject)
    return (body, subject)
    
#running server with SSL
if __name__ == "__main__":
    log = logging.getLogger("werkzeug")
    app.run(ssl_context="adhoc")
