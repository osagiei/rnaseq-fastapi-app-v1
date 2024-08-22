import boto3
import pandas as pd
import pymysql


def tau_method(expression_values):
    max_expr = max(expression_values)
    tau = sum(1 - (x / max_expr)
              for x in expression_values) / (len(expression_values) - 1)
    return tau


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = 'cf-templates-1uuth22f8zph-eu-west-2'
    key = event['Records'][0]['s3']['object']['key']

    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))

    conn = pymysql.connect(
        host='rnaseq-v1.cluster-cbguauu4ke0z.eu-west-2.rds.amazonaws.com',
        user='admin',
        password='nakwoshi1567',
        db='rnaseq_db')
    cursor = conn.cursor()

    for gene in df['gene_name'].unique():
        gene_df = df[df['gene_name'] == gene]
        expression_values = gene_df.iloc[:, 1:].sum(axis=1).values

        tau = tau_method(expression_values)

        cursor.execute("""
            INSERT INTO tissue_specificity (gene_name, tau, analysis_id)
            VALUES (%s, %s, %s)
        """, (gene, tau, event['analysis_id']))

        biotype_counts = gene_df['biotype'].value_counts(normalize=True)
        for biotype, proportion in biotype_counts.items():
            cursor.execute("""
                INSERT INTO tissue_complexity (gene_biotype, proportion, total_reads, analysis_id)
                VALUES (%s, %s, %s, %s)
            """, (biotype, proportion, sum(expression_values), event['analysis_id']))

    conn.commit()
    conn.close()
