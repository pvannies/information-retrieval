# Information Retrieval, vector search and its benchmarks

Welcome to the repository!

We will learn about
- smart search
- information retrieval
- embedding models
- vector database
- benchmark datasets
- information retrieval metrics
- vector search settings

You will run your own evaluation on this mini application consisting of the weaviate vector database filled with a benchmark dataset.

## Resources

- [Massive Text Embedding Benchmark Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Information about benchmark datasets](https://github.com/beir-cellar/beir)
- [Weaviate documentation](https://weaviate.io/developers/weaviate)
  - [Hybrid search](https://weaviate.io/developers/weaviate/search/hybrid)
  - [text2vec-transformers](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-transformers)
  - [Collection schema](https://weaviate.io/developers/weaviate/config-refs/schema)
  - [Getting started with Weaviate Python Library](https://towardsdatascience.com/getting-started-with-weaviate-python-client-e85d14f19e4f)

- [MTEB paper](references/"MTEB, Massive Text Embedding Benchmark.pdf")
- [BEIR paper](references/"BEIR, A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models.pdf")


## Prerequisites

* Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for your operating system. Request the docker desktop license here: https://ordina.4me.com/self-service
* Run `docker-compose build` in the root of this repository.
* Run `docker-compose up` in the root of this repository.

Test by going to http://localhost:8080/v1 if the weaviate database has started.

* Have package manager [poetry](https://python-poetry.org/docs/) installed
* Have Python 3.11 installed
* (if you want the venv to be in this repo, first set `poetry config virtualenvs.in-project true`)
* run `poetry install` in the root of this repository to create a venv 


## Try it out

- unzip the scifact to the datasets folder.
- perform the prerequisites as described above
- run `ingestion.py`
- run `evaluation.py`

## Ideas
- Experiment with weaviate vector search parameters in `evaluation.py`
- Change the embedding model in the build args in the `docker-compose.yaml`
- Investigate another dataset