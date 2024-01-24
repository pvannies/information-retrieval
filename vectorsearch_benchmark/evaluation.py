import pytrec_eval
import logging
import json
import os
from datetime import datetime

from weaviate import Client
from typing import List, Dict, Tuple
from ingestion import connect_to_client, DATASET_NAME, WEAVIATE_CLASS_NAME, WEAVIATE_URL
from data_loader import GenericDataLoader
from util import time_it

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# What other properties could be interesting to alter?
ALPHA = 0.75
BM25_PROPERTIES = ["text"]
EMBEDDING_MODEL = 'multilingual-e5-small'
LIMIT_RESULTS = 20

# https://weaviate.io/developers/weaviate/search/hybrid
# Use the alpha argument to change how much each search affects the results.
#
# An alpha of 1 is a pure vector search.
# An alpha of 0 is a pure keyword search.


def query_and_retrieve_results(
        client: Client,
        query: str,
        limit: int = LIMIT_RESULTS,
        alpha: float = ALPHA,
        properties: list = BM25_PROPERTIES
) -> list:
    """Query the weaviate database and retrieve the results."""

    answer = (
        client.query.get(
            WEAVIATE_CLASS_NAME,
            ["corpus_id", "title", "text"],
        )
        .with_hybrid(query=query, properties=properties, alpha=alpha)
        .with_additional(["score"])
        .with_limit(limit)
        .do()
    )
    list_answers = answer["data"]["Get"][WEAVIATE_CLASS_NAME]
    return list_answers


# for evaluation, the results should be returned in the format:
# {"query_id": {"corpus_id_1": score, "corpus_id_2": score}, etc}
def convert_list_answers(list_answers: List[Dict]):
    results = {}
    for item in list_answers:
        corpus_id = item.get("corpus_id", "")
        score = float(item.get('_additional', {}).get('score', 0.))
        results[corpus_id] = score
    return results


@time_it
def get_results_dataset(client: Client, queries: Dict[str, str]) -> Dict[str, Dict[str, float]]:
    results_dict = {}
    for query_id, query in queries.items():
        list_answers = query_and_retrieve_results(client, query)
        top_results = convert_list_answers(list_answers)
        results_dict[query_id] = top_results
    return results_dict


# evaluation function comes from: https://github.com/beir-cellar/beir/blob/main/beir/retrieval/evaluation.py
# couldn't install beir directly because of error in dependancy pytrec_eval
# pytrec_eval is now correctly installed with poetry using the fixed library pytrec-eval-terrier
def evaluate(qrels: Dict[str, Dict[str, int]],
             results: Dict[str, Dict[str, float]],
             k_values: List[int],
             ignore_identical_ids: bool = True) -> Tuple[
    Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float]]:
    if ignore_identical_ids:
        logger.info(
            'For evaluation, we ignore identical query and document ids (default), '
            'please explicitly set ``ignore_identical_ids=False`` to ignore this.')
        popped = []
        for qid, rels in results.items():
            for pid in list(rels):
                if qid == pid:
                    results[qid].pop(pid)
                    popped.append(pid)

    ndcg = {}
    _map = {}
    recall = {}
    precision = {}

    for k in k_values:
        ndcg[f"NDCG@{k}"] = 0.0
        _map[f"MAP@{k}"] = 0.0
        recall[f"Recall@{k}"] = 0.0
        precision[f"P@{k}"] = 0.0

    map_string = "map_cut." + ",".join([str(k) for k in k_values])
    ndcg_string = "ndcg_cut." + ",".join([str(k) for k in k_values])
    recall_string = "recall." + ",".join([str(k) for k in k_values])
    precision_string = "P." + ",".join([str(k) for k in k_values])
    evaluator = pytrec_eval.RelevanceEvaluator(qrels, {map_string, ndcg_string, recall_string, precision_string})
    scores = evaluator.evaluate(results)

    for query_id in scores.keys():
        for k in k_values:
            ndcg[f"NDCG@{k}"] += scores[query_id]["ndcg_cut_" + str(k)]
            _map[f"MAP@{k}"] += scores[query_id]["map_cut_" + str(k)]
            recall[f"Recall@{k}"] += scores[query_id]["recall_" + str(k)]
            precision[f"P@{k}"] += scores[query_id]["P_" + str(k)]

    for k in k_values:
        ndcg[f"NDCG@{k}"] = round(ndcg[f"NDCG@{k}"] / len(scores), 5)
        _map[f"MAP@{k}"] = round(_map[f"MAP@{k}"] / len(scores), 5)
        recall[f"Recall@{k}"] = round(recall[f"Recall@{k}"] / len(scores), 5)
        precision[f"P@{k}"] = round(precision[f"P@{k}"] / len(scores), 5)

    for eval in [ndcg, _map, recall, precision]:
        logger.info("\n")
        for k in eval.keys():
            logger.info("{}: {:.4f}".format(k, eval[k]))

    return ndcg, _map, recall, precision


if __name__ == "__main__":
    # assumption: data is already in weaviate vector database
    client = connect_to_client(WEAVIATE_URL)

    data_path = f"./datasets/{DATASET_NAME}"
    dataset = data_path.split('/')[-1]
    _, queries, qrels = GenericDataLoader(data_path).load(split="test")  # or split = "train" or "dev"

    results = get_results_dataset(client, queries)

    ndcg, _map, recall, precision = evaluate(qrels, results, [1, 2, 5, 10])

    info_dict = {'dataset': dataset,
                 'embedding_model': EMBEDDING_MODEL,
                 'alpha': ALPHA,
                 'bm25_properties': BM25_PROPERTIES,
                 'ndcg': ndcg,
                 'map': _map,
                 'recall': recall,
                 'precision': precision}

    date = datetime.now().strftime('%d-%m-%Y-%H%M')
    filename = f"evaluation_metrics_{dataset}_{EMBEDDING_MODEL}_alpha={ALPHA}.json"
    with open(os.path.join('output', filename), 'w') as myfile:
        json.dump(info_dict, myfile, indent=4)
