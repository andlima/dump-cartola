from collections import namedtuple

import datetime
import io
import csv
import json

import boto3

import requests


base_url = 'http://api.cartolafc.globo.com'
mercado_url = 'atletas/mercado'
partidas_url = 'partidas/{}'

bucket_name = 'cartolafcbucket'


def get_url(bucket, url, save=True):
    today = datetime.date.today()
    raw = requests.get('{}/{}'.format(base_url, url)).content
    key = '{}/{}.json'.format(today, url)
    if save:
        bucket.put_object(Key=key, Body=raw)
    return json.loads(raw)


def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    mercado_full = get_url(bucket, mercado_url)

    rodada_id = mercado_full['atletas'][0]['rodada_id']

    partidas_full = get_url(bucket, partidas_url.format(rodada_id))

    Atleta = namedtuple(
        'Atleta',
        ('id,apelido,clube,posicao,status,'
         'pontos,preco,variacao,media,jogos,scout,rodada_id')
    )

    mapping = {
        table: {v['id']: v['nome']
                for v in mercado_full[table].values()}
        for table in ['clubes', 'posicoes', 'status']
    }

    atletas = [
        Atleta(
            item['atleta_id'],
            item['apelido'],
            mapping['clubes'][item['clube_id']],
            mapping['posicoes'][item['posicao_id']],
            mapping['status'][item['status_id']],
            item['pontos_num'],
            item['preco_num'],
            item['variacao_num'],
            item['media_num'],
            item['jogos_num'],
            item['scout'],
            item['rodada_id'],
        )
        for item in mercado_full['atletas']
    ]

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(Atleta._fields)
    writer.writerows(atletas)

    today = datetime.date.today()
    out_csv = out.getvalue().encode('utf-8')
    key_csv = '{}/{}/atletas.csv'.format(today, rodada_id)
    bucket.put_object(Key=key_csv, Body=out_csv)
