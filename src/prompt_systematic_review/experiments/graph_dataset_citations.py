import os
import pandas as pd
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from pdfminer.high_level import extract_text
from tqdm import tqdm
from prompt_systematic_review.config_data import DataFolderPath
import matplotlib.pyplot as plt

datasets = [
    "GSM8K",
    "Search_QA",
    "MMLU",
    "AQUA-RAT",
    "BIG-bench",
    "TruthfulQA",
    "CommonsenseQA",
    "QASC",
    "WinoGrande",
    "BBH",
    "HellaSwag",
]


def parse_pdf(file_path):
    try:
        text = extract_text(file_path)
        return text
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return ""


def process_file(args):
    folder_path, filename = args
    file_path = os.path.join(folder_path, filename)
    if filename.endswith(".pdf"):
        data = parse_pdf(file_path)
        counts = {
            dataset: data.count(dataset) for dataset in datasets if dataset in data
        }
        return filename, counts
    return filename, {}


def count_dataset_mentions_parallel(folder_path):
    files = os.listdir(folder_path)
    files = [f for f in files if f.endswith(".pdf")]

    with Pool(cpu_count()) as pool:
        result_iter = pool.imap_unordered(
            process_file, [(folder_path, f) for f in files]
        )

        dataset_counts = defaultdict(int)

        for _, counts in tqdm(result_iter, total=len(files)):
            for dataset, count in counts.items():
                dataset_counts[dataset] += count

    return dataset_counts


def graph_dataset_citations():
    papers_dataset_path = os.path.join(DataFolderPath, "papers/")
    dataset_usage_counts = count_dataset_mentions_parallel(papers_dataset_path)

    # Sorting the datasets based on usage count
    sorted_datasets = sorted(
        dataset_usage_counts.items(), key=lambda x: x[1], reverse=True
    )
    if not sorted_datasets:
        print("No datasets found in the papers.")
        return

    datasets, counts = zip(*sorted_datasets)

    plt.figure(figsize=(10, 6))
    plt.bar(datasets, counts, color="#2E8991")
    plt.xlabel("Dataset Name")
    plt.ylabel("Number of Mentions")
    plt.title("Dataset Mentions in Papers")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_dir = os.path.join(DataFolderPath, "experiments_output")
    os.makedirs(output_dir, exist_ok=True)
    # output_file_path = os.path.join(output_dir, "graph_dataset_mentions_output.png")
    output_file_path = os.path.join(output_dir, "graph_dataset_mentions_output.png")

    plt.savefig(output_file_path)


class Experiment:
    def run():
        graph_dataset_citations()


if __name__ == "__main__":
    graph_dataset_citations()
