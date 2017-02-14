import os
import json
import csv
import StringIO
import logging
import datetime

from flask import jsonify, request
import requests

from . import endpoints
from firesreport.responders import ErrorResponder
from firesreport.utils.http import request_to_microservice


@endpoints.route('/hello', methods=['GET'])
def say_hello():
    """Query GEE Dataset Endpoint"""
    logging.info('Doing GEE Query')
    return jsonify({'data': 'hello'}), 200


@endpoints.route('/firesreport', methods=['GET'])
def do_reports():
    """Do fires report documentation"""
    logging.info('started do_reports function')

    # grab query parameters
    # if any not found, set as none
    islands = request.args.get('islands', None)
    provinces = request.args.get('provinces', None)
    period = request.args.get('period', None)

    logging.info(request.args)

    if (not islands and not provinces) or not period:
        return jsonify({'errors': 
                           [{'status': '400', 
                            'title': 'must supply islands or provinces and period'}]}), 400

    if islands:
        islands = islands.split(',')
    else:
        provinces = provinces.split(',')

    period_list = period.split(',')

    if len(period_list) != 2:
        return jsonify({'errors':
                           [{'status': '400',
                            'title': 'period must have two arguments'}]}), 400

    if islands and provinces:
        return jsonify({'errors':
                           [{'status': '400',
                            'title': 'must supply only islands or provinces, not both'}]}), 400

    try:
        valid_from = datetime.datetime.strptime(period_list[0], '%Y-%m-%d')
        valid_to = datetime.datetime.strptime(period_list[1], '%Y-%m-%d')

    except ValueError:
        return jsonify({'errors':
                           [{'status': '400',
                            'title': 'invalid dates supplied, must match YYYY-MM-DD'}]}), 400

    if valid_from > valid_to:
        return jsonify({'errors':
                           [{'status': '400',
                            'title': 'invalid dates supplied, start date must be less than end'}]}), 400

    if islands:
        column = 'ISLAND'
        values = islands
    else:
        column = 'PROVINCE'
        values = provinces

    values = "'{}'".format("','".join(values))
    logging.debug(values)

    payload = {
        'f':'json',
        'spatialRelationship':'esriSpatialRelIntersects',
        'where': "{0} in ({1}) AND ACQ_DATE >= date '{2}' AND ACQ_DATE <= date '{3}'".format(column, values, period_list[0], period_list[1]),
        'returnGeometry':False,
        'groupByFieldsForStatistics':['ACQ_DATE'],
        'orderByFields':['ACQ_DATE ASC'],
        'outStatistics': "[{'onStatisticField':'ACQ_DATE','outStatisticFieldName':'Count','statisticType':'count'}]"
    }
    logging.info(payload)

    try:
        response = requests.get('http://gis-potico.wri.org/arcgis/rest/services/Fires/FIRMS_ASEAN/MapServer/0/query?', params=payload)
    except Error:
        return jsonify({'errors': [{
            'status': '500',
            'title': 'Service unavailable'
            }]
        }), 500

    return jsonify(response.json()), 200    



