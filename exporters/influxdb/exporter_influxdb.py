from datetime import timedelta

import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

#  ================================================================================
# config = configparser.ConfigParser()
#
# config.read('configs/config.ini')
#
# output_data_csv = config['FilePaths']['OutputData']

configfile = "exporters/influxdb/configs/influxdb_config.ini"
client = InfluxDBClient.from_config_file(configfile)

bck = 'tbk-1'
org = 'test_org'


# for i in range(500):
#     perc = random.uniform(0,100)
#     print(perc)
#     data = ('mem,host=host1 used_percent=%s' % perc)
#     write_api.write(bucket, org, data)
#     time.sleep(1)

def write_data(data):
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Data format line protocol:
    # measurementName, tagKey = tagValue fieldKey = "fieldValue" 1465839830100400200
    # ---------------    ---------------   ---------------------  -------------------
    #       |                   |                   |                    |
    #  Measurement            Tag set            Field set           Timestamp

    write_api.write(bucket=bck, org=org, record=data)

    write_api.__del__()


def write_dataframe(dataframe: pd.DataFrame, measurement: str,  tags: list = None):

    write_api = client.write_api(write_options=SYNCHRONOUS)

    write_api.write(bucket=bck, org=org, record=dataframe,
                    data_frame_measurement_name=measurement, data_frame_tag_columns=tags)

    write_api.__del__()


def write_dataframe_from_csv(data_csv):
    data_frame = pd.read_csv(filepath_or_buffer=data_csv, index_col='timestamp')
    print(data_frame)

    write_api = client.write_api(write_options=SYNCHRONOUS)

    # p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
    # p = influxdb_client.Point("stocks_info_2").tag("stock_symbol", "ASA").field("price", 123)
    # write_api.write(bucket=bucket, org=org, record=p)

    now = pd.Timestamp.utcnow()
    _data_frame = pd.DataFrame(data=[["coyote_creek", 1.0], ["coyote_creek", 2.0]],
                               index=[now, now + timedelta(hours=1)],
                               columns=["location", "water_level"])
    print(_data_frame)

    # write_api.write(bucket=bck, org=org, record=_data_frame,
    #                 data_frame_measurement_name='h2o_feet', data_frame_tag_columns=['location'])
    #
    write_api.write(bucket=bck, org=org, record=data_frame,
                    data_frame_measurement_name='stocks_info_3', data_frame_tag_columns=['stock_symbol'])

    write_api.__del__()


# _write_client.__del__()
# _client.__del__()

def delete_data():
    data = 'test'
    delete_api = client.delete_api(data)
