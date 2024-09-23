from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowNotFoundException
from io import BytesIO
import requests
import json
from minio import Minio

BUCKET_NAME = 'stock-market'

def get_minio_client():
    minio = BaseHook.get_connection('minio')
    print(minio)
    client = Minio(
        endpoint = minio.extra_dejson['endpoint_url'].split('//')[1],
        access_key = minio.login,
        secret_key = minio.password,
        secure = False
    )
    return client


def _get_stock_prices(url, symbol):
    "fetch stock prices for apple"

    url = f"{url}{symbol}?metrics=high?&interval=1d&range=1y"
    api = BaseHook.get_connection('stock_api')
    response = requests.get(url, headers=api.extra_dejson['headers'])
    return json.dumps(response.json()['chart']['result'][0])


def _store_prices(stock):
    "Store the stock market prices in MinIo, which is hosted inside docker container"

    client = get_minio_client()

    # create bucket if not exists
    
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)

    stock = json.loads(stock)
    symbol = stock['meta']['symbol']
    data = json.dumps(stock, ensure_ascii = False).encode('utf8')

    # write to MinIO
    objw = client.put_object(
        bucket_name = BUCKET_NAME,
        object_name = f'{symbol}/prices.json',
        data = BytesIO(data),
        length = len(data)
    )

    return f'{objw.bucket_name}/{symbol}'


def _get_formatted_csv(path):

    client = get_minio_client()
    prefix_name = f"{path.split('/')[1]}/formatted_prices/"
    objects = client.list_objects(
        bucket_name = BUCKET_NAME, 
        prefix = prefix_name,
        recursive = True
    )

    for object in objects:
        if object.object_name.endswith('.csv'):
            return object.object_name
    raise AirflowNotFoundException('The csv file does not exists in MinIO')
