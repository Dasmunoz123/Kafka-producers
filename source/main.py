import pandas as pd
import json, time
from utils import build_schema, build_payload, load_events, KafkaProducer

## kafka endpoint data configuration
weather_file = './data/synthetic_strokes.csv'
productor_tipo = "nowcast"      # {nowcast - linet - alisios}
producer_config = {
    'name':'synthetic-dev',
    'bootstrap.server':'kafka:9092',
    'topic':'syntetic-weather',
    'timeout.seconds':10
    }
producer = KafkaProducer(conf=producer_config)
producer_schema = build_schema(name=producer_config['name'], tipo=productor_tipo)

# main execution
if __name__ == '__main__':
    for chunk in pd.read_csv(filepath_or_buffer = weather_file, parse_dates = ['timestamp'], dayfirst=True, chunksize=1):
        current_time = pd.Timestamp.now() + pd.Timedelta(hours=5)
        chunk['timestamp'] = current_time.strftime(format='%Y-%m-%dT%H:%M:%S.000Z')
        chunk.columns = ['@' + col for col in chunk.columns]
        chunk = chunk.astype('string')

        values = []
        for idx, row in chunk.iterrows():
            s = build_payload(tipo=productor_tipo,row=row)
            values.append(s)
        
        load_events(producer=producer, values=values, schema=producer_schema)
        print("Evento cargado")
        print(values)
        time.sleep(15)