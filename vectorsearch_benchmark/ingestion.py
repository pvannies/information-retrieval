from weaviate import Client
from data_loader import GenericDataLoader

WEAVIATE_URL = "http://localhost:8080"
WEAVIATE_CLASS_NAME = "Document"
DATASET_NAME = 'scifact'
TEXT = "text"

# https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules
# Weaviate generates vector embeddings at the object level (rather than for individual properties).

def connect_to_client(host: str):
    """Connect to local client of Weaviate vector database.

    Returns
    -------
    Weaviate.Client
    """
    client = Client(host)
    return client


def create_schema(client: Client):
    """Create a schema in the db, if not yet existing.

    The schema definition contains the source, pagenumber and content of the chunk
    """
    if client.schema.exists(WEAVIATE_CLASS_NAME):
        client.schema.delete_all()
    # https://weaviate.io/developers/weaviate/manage-data/collections
    schema = {
        "class": WEAVIATE_CLASS_NAME,
        "description": "BEIR datasets format",
        "properties": [
            {
                "name": "corpus_id",
                "dataType": ["int"],
            },
            {
                "name": "title",
                "dataType": [TEXT],
            },
            {
                "name": "text",
                "dataType": [TEXT],
            },
            {
                "name": "dataset",
                "dataType": ["string"],
            },
            {
                "name": "language",
                "dataType": ["string"],
            }
        ],
        "moduleConfig":
            {"vectorizeClassName": False}
    }

    client.schema.create('schema.json')


def ingest_data(client: Client, dataset_name: str):
    corpus, _, _ = GenericDataLoader(f"datasets/{dataset_name}").load(split="test")  # or split = "train" or "dev"
    nr = 0

    client.batch.configure(batch_size=100)

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
            print(f"{nr} importing corpus_id {corpus_id}: {title}")

        batch.flush()
        # ensure that last batch is flushed


def count_objects(client: Client, class_name=WEAVIATE_CLASS_NAME):
    response = client.query.aggregate(class_name).with_meta_count().do()
    actual_count = response["data"]["Aggregate"][class_name][0]["meta"]["count"]
    print(f"There are {actual_count} of {class_name} items in the vector database")
    return actual_count


if __name__ == "__main__":
    client = connect_to_client(WEAVIATE_URL)
    create_schema(client)
    ingest_data(client, DATASET_NAME)
    count_objects(client)
