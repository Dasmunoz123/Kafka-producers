import time, json
from uuid import uuid4
from confluent_kafka import Producer
from shapely import Point, wkb

## To load elements and push it into kafka topic
def load_events(producer, values, schema):
    for value in values:
            producer.producer.produce(producer.topic, value=json.dumps(obj={"schema": schema, "payload":value}))
    producer.producer.flush(timeout=producer.timeout)


def build_schema(name, tipo):
    if tipo == "nowcast":
        EVENT_SCHEMA = {
            "type": "struct",
                "name": name + '.Value',
                "fields": [
                    { "type": "string", "optional"  : False, "field": "fecha"},
                    { "type": "string", "optional"  : False, "field": "coordenadas"},
                    { "type": "string", "optional"  : False, "field": "altura"},
                    { "type": "string", "optional" : False, "field": "tipo"},
                    { "type": "string", "optional" : False, "field": "corriente"},
                    { "type": "string", "optional" : False, "field": "polaridad"},
                    { "type": "string", "optional" : False, "field": "error"},
                    { "type": "string", "optional" : False, "field": "didt"}
                ]
            }
    elif tipo == "linet":
        EVENT_SCHEMA = {
            "type": "struct",
                "name": name + '.Value',
                "fields": [
                    { "type": "int64", "optional"   : False, "field": "id"},
                    { "type": "string", "optional"  : False, "field": "fecha"},
                    { "type": "string", "optional"  : False, "field": "geom_str"},
                    { "type": "float64", "optional" : False, "field": "corriente"}
                ]
            }
    elif tipo == "alisios":
        EVENT_SCHEMA = {
            "type": "struct",
                "name": name + '.Value',
                "fields": [
                    { "type": "int64", "optional"   : False, "field": "id"},
                    { "type": "string", "optional"  : False, "field": "fecha"},
                    { "type": "int64", "optional"   : False, "field": "hours_ahead"},
                    { "type": "string", "optional"  : False, "field": "geom_str"},
                    { "type": "float64", "optional" : False, "field": "cg_light"},
                    { "type": "float64", "optional" : False, "field": "u_10_m_tr"},
                    { "type": "float64", "optional" : False, "field": "v_10_tr"},
                    { "type": "float64", "optional" : False, "field": "precip_tot"}
                ]
            }
    elif tipo == "TWS":
        EVENT_SCHEMA = {
            "type": "struct",
                "name": name + '.Value',
                "fields": [
                    { "type": "int64", "optional"   : False, "field": "id"},
                    { "type": "string", "optional"  : False, "field": "fecha"},
                    { "type": "string", "optional"  : False, "field": "geom_str"},
                    { "type": "float64", "optional" : False, "field": "ce"},
                    { "type": "float64", "optional" : False, "field": "dce"}
                ]
            }
    else:
        EVENT_SCHEMA = {}
    return EVENT_SCHEMA


def build_payload(tipo, row):
    if tipo == 'nowcast':
        EVENT_PAYLOAD = {
            "fecha":row['@timestamp'],
            "coordenadas":{"lat"   : float(row['@y']),"lon"  : float(row['@x'])},
            "altura":float(row['@height']),
            "tipo":'NT' if int(row['@type']) == 1 else 'NN',
            "corriente":abs(float(row['@amplitude'])),
            "polaridad":'POS' if float(row['@amplitude']) > 0 else 'NEG', 
            "error":row['@locationError'],
            "didt":0.0
        }
    
    elif tipo == "linet":
        EVENT_PAYLOAD = {
            "id"        : str(object=uuid4()),
            "fecha"     : row['@timestamp'], 
            "geom_str"  : wkb.dumps(Point(row['@x'], row['@y']), hex=True),
            "corriente" : float(row['@amplitude'])
        }

    elif tipo == "alisios":
        EVENT_PAYLOAD = {
            "id":str(object=uuid4()),
            "fecha":row['@timestamp'], 
            "geom_str":wkb.dumps(Point(row['@x'], row['@y']), hex=True),
            "hours_ahead":6,
            "cg_light":float(row['@amplitude']),
            "u_10_m_tr":float(row['@amplitude']),
            "v_10_tr":float(row['@amplitude']),
            "precip_tot":float(row['@amplitude'])
        }
    
    elif tipo == "TWS":
        EVENT_PAYLOAD = {
            "id":str(object=uuid4()),
            "fecha":row['@timestamp'], 
            "geom_str":wkb.dumps(Point(row['@x'], row['@y']), hex=True),
            "ce":float(row['@amplitude']),
            "dce":float(row['@amplitude'])
        }
    
    else: 
        EVENT_PAYLOAD = {}
    return EVENT_PAYLOAD


class KafkaProducer:
    def __init__(self, conf):
        self.name = conf['name']
        self.producer = Producer({'bootstrap.servers': conf['bootstrap.server']})
        self.topic = conf['topic']
        self.timeout = conf['timeout.seconds']