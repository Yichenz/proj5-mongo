"""
    Flask web app connects to Mongo database.
    Keep a simple list of dated memoranda.
    
    Representation conventions for dates:
    - In the session object, date or datetimes are represented as
    ISO format strings in UTC.  Unless otherwise specified, this
    is the format passed around internally. Note that ordering
    of ISO format strings is consistent with date/time order
    - User input/output is in local (to the server) time
    - Database representation is as MongoDB 'Date' objects
    Note that this means the database may store a date before or after
    the date specified and viewed by the user, because 'today' in
    Greenwich may not be 'today' here.
    """

import flask
from flask import render_template
from flask import request
from flask import url_for

import json
import logging

# Date handling
import arrow # Replacement for datetime, based on moment.js
import datetime # But we may still need time
from dateutil import tz  # For interpreting local times

# Mongo database
from pymongo import MongoClient, DESCENDING
from bson import ObjectId


###
# Globals
###
import config

app = flask.Flask(__name__)

try:
    dbclient = MongoClient(config.MONGO_URL)
    db = dbclient.memos
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)

import uuid
app.secret_key = str(uuid.uuid4())

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    flask.session['memos'] = get_memos()
    for memo in flask.session['memos']:
        app.logger.debug("Memo: " + str(memo))
    return flask.render_template('index.html')

@app.route("/create_memo", methods=["POST"])
def create_memo():
    app.logger.debug("Create memo entry")
    
    time = request.form['time']
    text = request.form['text']
    
    try:
        dt = arrow.get(time, 'MM/DD/YYYY').replace(days=+1)
    except:
        return 'params invalid'
    put_memo(dt, text);
    \
    return "ok"

@app.route("/remove_memo", methods=["POST"])
def remove_memo():
    app.logger.debug("Remove memo entry")
    # first get params from form
    id = request.form['id']
    # remove memo
    del_memo(id)
    return "ok"


# We don't have an interface for creating memos yet
# @app.route("/create")
# def create():
#     app.logger.debug("Create")
#     return flask.render_template('create.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#################
#
# Functions used within the templates
#
#################

# NOT TESTED with this application; may need revision
#@app.template_filter( 'fmtdate' )
# def format_arrow_date( date ):
#     try:
#         normal = arrow.get( date )
#         return normal.to('local').format("ddd MM/DD/YYYY")
#     except:
#         return "(bad date)"

@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
        Date is internal UTC ISO format string.
        Output should be "today", "yesterday", "in 5 days", etc.
        Arrow will try to humanize down to the minute, so we
        need to catch 'today' as a special case.
        """
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        if then.date() == now.date():
            human = "Today"
        else:
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except:
        human = date
    return human


#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
        Returns all memos in the database, in a form that
        can be inserted directly in the 'session' object.
        """
    records = [ ]
    
    for record in collection.find({"type": "dated_memo"}).sort('date',
                                                               DESCENDING):
        record['date'] = arrow.get(record['date']).isoformat()
        
        record['id'] = '%s' % record['_id']
        del record['_id']
        records.append(record)
    return records


def put_memo(dt, mem):
    """
        Place memo into database
        Args:
        dt: Datetime (arrow) object
        mem: Text of memo
        NOT TESTED YET
        """
    record = { "type": "dated_memo",
        "date": dt.to('utc').naive,
        "text": mem,
    }
    collection.insert(record)
    return

def del_memo(id):
    """
        Remove memo from database
        Args:
        id: Mongodb _id
        """
    collection.remove({'_id': ObjectId(id)})
    return;


if __name__ == "__main__":
    # App is created above so that it will
    # exist whether this is 'main' or not
    # (e.g., if we are running in a CGI script)
    app.debug=config.DEBUG
    app.logger.setLevel(logging.DEBUG)
    # We run on localhost only if debugging,
    # otherwise accessible to world
    if config.DEBUG:
        # Reachable only from the same computer
        app.run(port=config.PORT)
    else:
        # Reachable from anywhere 
        app.run(port=config.PORT,host="0.0.0.0")


