import logging
from util import time_it
from weaviate import Client
from data_loader import GenericDataLoader

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BATCH_SIZE = 100
WEAVIATE_URL = "http://localhost:8080"
WEAVIATE_CLASS_NAME = "Document"
DATASET_NAME = 'scifact'
TEXT = "text"


def connect_to_client(host: str):
    client = Client(host)
    return client


def create_schema(client: Client):

    if client.schema.exists(WEAVIATE_CLASS_NAME):
        client.schema.delete_all()

    client.schema.create('schema.json')


def log_properties_schema(client: Client):
    schema = client.schema.get()
    properties = schema['classes'][0].get('properties')
    logger.info('schema consists of properties:')
    for item in properties:
        logger.info({'name': item['name'], 'dataType': item['dataType'],
               'skip': item['moduleConfig']['text2vec-transformers']['skip']})


def ingest_data(client: Client, dataset_name: str):
    corpus, _, _ = GenericDataLoader(f"datasets/{dataset_name}").load(split="test")  # or split = "train" or "dev"
    nr = 0

    client.batch.configure(batch_size=BATCH_SIZE)

    with client.batch as batch:
        for corpus_id, content in corpus.items():
            title = content.get("title", "")
            properties = {
                "corpus_id": corpus_id,
                "title": title,
                "text": content.get("text", ""),
                "language": "english",
                "dataset": dataset_name}
            batch.add_data_object(properties, "Document")
            nr += 1
            if nr % 10 == 0:
                logger.info(f"{nr} importing corpus_id {corpus_id}: {title}")

        batch.flush()
        # ensure that last batch is flushed


@time_it
def count_objects(client: Client, class_name=WEAVIATE_CLASS_NAME):
    response = client.query.aggregate(class_name).with_meta_count().do()
    actual_count = response["data"]["Aggregate"][class_name][0]["meta"]["count"]
    logger.info(f"There are {actual_count} of {class_name} items in the vector database")
    return actual_count


if __name__ == "__main__":
    client = connect_to_client(WEAVIATE_URL)
    create_schema(client)
    log_properties_schema(client)
    ingest_data(client, DATASET_NAME)
    count_objects(client)
