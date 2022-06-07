#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ZMQ client to gather events, attributes or sighting updates
# from a MISP instance and push them to an InfluxDB instance.
#

import argparse
import json
import zmq
import logging
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS

logging.basicConfig(stream=sys.stdout,
                    format="[%(levelname)s] [%(asctime)s] - %(message)s",
                    level=logging.INFO)


def push_metric(api, instance, topic, m, recv_ts):
    if topic == "misp_json_audit" and "AuditLog" in m:
        logging.info("AuditLog pushed to InfluxDB")
        api.write(bucket="misp", record={
            "measurement": "audit",
            "tags": {
                "model": m["AuditLog"]["model"].lower(),
                "action": m["AuditLog"]["action"].lower(),
                "instance": instance
            },
            "fields": {
                "ip": m["AuditLog"].get("ip", ""),
                "event_id": str(m["AuditLog"].get("event_id", "")),
                "model_id": str(m["AuditLog"].get("model_id", "")),
                "model_title": str(m["AuditLog"].get("model_title", "")),
            },
        })

    if topic == "misp_json_audit" and "Log" in m:
        logging.info("Log pushed to InfluxDB")
        r = {
            "measurement": "audit",
            "tags": {
                "model": m["Log"]["model"].lower(),
                "action": m["Log"]["action"].lower(),
                "instance": instance
            },
            "fields": {
                "ip": m["Log"].get("ip", ""),
                "email": str(m["Log"].get("email", "")),
                "user_id": str(m["Log"].get("user_id", "")),
                "org": str(m["Log"].get("org", "")),
                "model_id": str(m["Log"].get("model_id", ""))
            },
            "time": int(datetime.strptime(m["Log"]["created"], '%Y-%m-%d %H:%M:%S').strftime("%s")) * 1000000000
        }

        api.write(bucket="misp", record=r)

    if topic == "misp_json_event" and "Event" in m:
        logging.info("Event pushed to InfluxDB")
        r = {
            "measurement": "event",
            "tags": {
                "instance": instance
            },
            "fields": {
                "id": m["Event"].get("id", ""),
                "published": str(m["Event"].get("published", False)),
                "info": m["Event"].get("info", "")
            },
            "time": int(float(m["Event"].get("timestamp", recv_ts)) * 1000000000)
        }
        if "Orgc" in m:
            r["fields"]["org"] = m["Orgc"].get("name", "")
            r["fields"]["org_id"] = m["Orgc"].get("id", "")

        api.write(bucket="misp", record=r)

    if topic == "misp_json_attribute" and "Attribute" in m:
        logging.info("Attribute pushed to InfluxDB")
        api.write(bucket="misp", record={
            "measurement": "attribute",
            "tags": {
                "category": m["Attribute"].get("category", "").lower(),
                "type":  m["Attribute"].get("type", "").lower(),
                "instance": instance
            },
            "fields": {
                "id": m["Attribute"].get("id", ""),
                "event_id": str(m["Attribute"].get("event_id", "")),
                "value1": m["Attribute"].get("value1", ""),
                "value2": m["Attribute"].get("value2", ""),
                "to_ids": str(m["Attribute"].get("to_ids", False)),
            },
            "time": int(float(m["Attribute"].get("timestamp", recv_ts)) * 1000000000)
        })

    if topic == "misp_json_sighting" and "Sighting" in m:
        logging.info("Sighting pushed to InfluxDB")
        api.write(bucket="misp", record={
            "measurement": "sighting",
            "tags": {
                "category": m["Attribute"].get("category", "").lower(),
                "type":  m["Attribute"].get("type", "").lower(),
                "false_positive":  m["Sighting"].get("type", ""),
                "instance": instance
            },
            "fields": {
                "id": m["Sighting"].get("id", ""),
                "event_id": str(m["Sighting"].get("event_id", "")),
                "value1": m["Sighting"].get("value1", ""),
                "value2": m["Sighting"].get("value2", ""),
                "to_ids": str(m["Sighting"].get("to_ids", False)),
            },
            "time": int(float(m["Sighting"].get("date_sighting", recv_ts)) * 1000000000)
        })

    if topic == "misp_json_self" and "status" in m:
        logging.info("ZMQ status pushed to InfluxDB")
        api.write(bucket="misp", record={
            "measurement": "zmq_status",
            "tags": {
                "instance": instance
            },
            "fields": {
                "uptime": m["uptime"],
            }
        })

    # TODO: handle this topics
    # misp_json_user
    # misp_json_object
    # misp_json_organisation
    # misp_json_object_reference
    # misp_json_conversation
    # misp_json_tag

def main():

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(description='A script to push MISP ZeroMQ messages to InfluxDB')
    parser.add_argument('-id', '--instance-id', required=False, dest='instance', help='The MISP instance global tag to apply to the metrics', default="prod")
    parser.add_argument('-u', '--url', required=False, dest='zmqurl', help='The ZeroMQ publisher to connect to', default=os.getenv("MISP_ZMQ_URL"))
    args = parser.parse_args()

    # ZMQ client
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(args.zmqurl)
    socket.setsockopt(zmq.SUBSCRIBE, b'')

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    logging.info("Subscribed to ZMQ")

    # InfluxDB client
    client = InfluxDBClient(
        url=os.getenv("INFLUXDB_URL"),
        token=os.getenv("INFLUXDB_TOKEN"),
        org=os.getenv("INFLUXDB_ORG")
    )
    api = client.write_api(write_options=ASYNCHRONOUS)

    while True:
        socks = dict(poller.poll(timeout=None))
        if socket in socks and socks[socket] == zmq.POLLIN:
            message = socket.recv()
            topic, s, m = message.decode('utf-8').partition(" ")
            logging.info("Received message from topic: {}".format(topic))

            try:
                push_metric(api, args.instance, topic, json.loads(m), time.time())
            except Exception as ex:
                logging.error("Failed to push metric: %s" % m, ex)


if __name__ == '__main__':
    main()
