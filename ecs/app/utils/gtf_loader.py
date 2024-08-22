import pandas as pd
import os
import subprocess
from sqlalchemy import create_engine


def download_gtf(gtf_url, output_path):
    subprocess.run(['wget', '-q', '-O', output_path, gtf_url], check=True)


def parse_and_load_gtf(DBUSER, DBPASSWORD, DBHOST, DBPORT, DBNAME, gtf_url):
    gtf_path = "/tmp/gtf_file.gtf.gz"

    download_gtf(gtf_url, gtf_path)

    engine = create_engine(
        f'mysql+mysqlconnector://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{DBNAME}')

    df = pd.read_csv(
        gtf_path,
        sep='\t',
        comment='#',
        header=None,
        compression='gzip')

    df.columns = [
        'seqname',
        'source',
        'feature',
        'start',
        'end',
        'score',
        'strand',
        'frame',
        'attributes']

    genes = df[df['feature'] == 'gene']

    def parse_attributes(attributes):
        gene_id = ''
        gene_name = ''
        biotype = ''
        description = ''
        if 'gene_id "' in attributes:
            gene_id = attributes.split('gene_id "')[1].split('"')[0]
        if 'gene_name "' in attributes:
            gene_name = attributes.split('gene_name "')[1].split('"')[0]
        if 'gene_biotype "' in attributes:
            biotype = attributes.split('gene_biotype "')[1].split('"')[0]
        if 'gene_description "' in attributes:
            description = attributes.split('gene_description "')[
                1].split('"')[0]
        return gene_id, gene_name, biotype, description

    gene_df = genes.apply(lambda x: pd.Series({
        'coord_id': f"{x['seqname']}:{x['start']}-{x['end']}:{x['strand']}",
        'chromosome': x['seqname'],
        'chrom_start': x['start'],
        'chrom_end': x['end'],
        'strand': x['strand'],
        'ensembl_id': parse_attributes(x['attributes'])[0],
        'gene_name': parse_attributes(x['attributes'])[1],
        'biotype': parse_attributes(x['attributes'])[2],
        'description': parse_attributes(x['attributes'])[3]
    }), axis=1)

    gene_df.drop_duplicates(subset='coord_id', inplace=True)

    gene_df.to_sql('gene', con=engine, if_exists='append', index=False)

    print(f"Loaded {len(gene_df)} genes into the database.")

    os.remove(gtf_path)
