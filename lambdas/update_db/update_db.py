import boto3
import pandas as pd
import pymysql
import io
import json


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = 'cf-templates-1uuth22f8zph-eu-west-2'
    #key = event['Records'][0]['s3']['object']['key']

    payload = json.loads(event['Records'][0]['body'])
    key = payload['s3_key']
    analysis_id = payload['analysis_id']
    #user_id = payload['user_id']

    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()), index_col=0)

    conn = pymysql.connect(
        host='rnaseq-v1.cluster-cbguauu4ke0z.eu-west-2.rds.amazonaws.com',
        user='admin',
        password='nakwoshi1567',
        db='rnaseq_db')
    cursor = conn.cursor()

    #analysis_id = event['analysis_id']

    for sample_id in df.columns:
        cursor.execute("""
            INSERT INTO sample (sample_id, sample_description, sample_type, sample_source)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE sample_description=VALUES(sample_description),
                                    sample_type=VALUES(sample_type),
                                    sample_source=VALUES(sample_source)
        """, (sample_id, "", "", ""))

    for gene_name, row in df.iterrows():
        for sample_id, raw_count in row.items():
            cursor.execute("""
                INSERT INTO gene_expression (raw_count, TPM, FPKM, RPKM, gene_name, sample_id, analysis_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (raw_count, None, None, None, gene_name, sample_id, analysis_id))

    conn.commit()
    conn.close()
