# Vector search and its benchmarks

Welcome to the repository!

We will learn about
- smart search
- embedding models
- vector database
- information retrieval
- benchmark datasets
- information retrieval metrics
- vector search settings

You will run your own evaluation on this mini application consisting of the weaviate vector database filled with a benchmark dataset.


# Running locally

* Install Docker Desktop for your operating system. Request the docker desktop license here: https://ordina.4me.com/self-service
* 
* Run `docker-compose build` in the root of this repository. You have to rebuild containers every time something changes in the Dockerfile or the dependencies (it caches so it doesn't rebuild everything).
* Run `docker-compose up` in the root of this repository.

test by going to http://localhost:8080/v1 if the weaviate database started.

Docker compose publishes the following ports:
* 8080: weaviate REST