'''
Defines the views of the dashboard.
This defines the interaction points, but the actual logic is treated
by the :mod:`controller`.
'''

from flask import current_app, Blueprint, render_template
from flask import jsonify
#from lxml import objectify
import dateutil.parser
import json

from requests import RequestException, ConnectionError

from dashboard_app import controller

#Logging
from logging import getLogger
from simplejson.scanner import JSONDecodeError
LOG = getLogger(__name__)

#Blueprint
dashboard = Blueprint('dashboard', __name__, url_prefix='')

@dashboard.route('/error')
def error():
    return render_template("error.html",
                           title='Error')


@dashboard.route('/')
@dashboard.route('/index')
@dashboard.route('/events/', methods = ['GET'])
@dashboard.route('/events', methods = ['GET'])
def index():
    '''
    Lists gaming sessions available to be followed.
    '''
    session_list = []
    try:
        events_controller = controller.EventsController()
        
        result = events_controller.get_sessions()
        
        items = result['items']
        count = result['count']
        
        LOG.debug(items)
        
        items_sorted = sorted(items, key=lambda d: dateutil.parser.parse(d['created']), reverse = True)
        
        return render_template("index.html", session_list = items_sorted, 
                               count = count, title='Dashboard Home')
    except RequestException as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error', error=str(e))    
    except Exception as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error', error='Unknown error. The developer has been notified.')        
    
    



@dashboard.route('/events/<sessionid>', methods = ['GET'])
def events(sessionid):
    '''
    Lists game events related to a given *sessionid*.
    :param sessionid:
    '''
    events_list = []
    try:
        events_controller = controller.EventsController()
        result = events_controller.get_events(sessionid)
        if result:
            try:
                for event in result["events"]:
                    #LOG.debug(event)
                    formatted_event = _format_event(event)
                    #LOG.debug(formatted_event)
                    events_list.append(formatted_event)
            except (AttributeError,KeyError,JSONDecodeError):
                return render_template("error.html",
                       title='Error',
                       error='Error reading the list of events from service.')

    except ConnectionError as e:
        return render_template("error.html",
                           title='Error',
                           error='Connection error. Is the game events service up?')

    except Exception as e:
        LOG.error(e.args, exc_info=True)
        return render_template("error.html",
                           title='Error',
                           error=e.args)

    #Sort by timestamp desc
    events_list_sorted = sorted(events_list, key=lambda d: d['timestamp'], reverse = True)  
            
    return render_template('events.html', events = events_list_sorted, sessionid=sessionid)



def _format_event(event):
    '''
    Internal helper function to clean up fields in the event before sending to template.
    :param event:
    '''
    
    
    if not ("level" in event):
        event["level"] = "==Not in a level=="
    else:
        if (event["level"] == ""):
            event["level"] = "==Not in a level=="
    
    if not ("timestamp" in event):
        event["timestamp"] = "==No timestamp=="
    else:
        if (event["timestamp"] == ""):
            event["timestamp"] = "==No timestamp=="        
        
    if not ("action" in event):
        event["action"] = "==No action=="
    else:
        if event["action"] =="":
            event["action"] = "==No action=="
    
    if not ("update" in event):
        event["update_string"] = ""
    else:
        event["update_string"] = event["update"]
        event.pop("update", None)
        
    if not ("result" in event):
        event["result"] = {}
    else:
        #LOG.debug(event["result"])
        if len(event["result"])>0:
            event["result"] = event["result"][0]
        else:
            event["result"] = {}

    return(event)

    