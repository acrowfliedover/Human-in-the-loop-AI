"""Retrain the Assignment 9 classifier on the Module 10 label revisions.

The model, vectorizer, hyperparameters, metric definitions, and 20/10 split
seeds match Module_9_assignment/baseline_classifier.ipynb. The only intended
change is the training label on records whose Module 10 majority label differs
from expand_other. Records that were not in the Module 10 form keep expand_other.
"""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.pipeline import Pipeline

TRAIN_SIZE = 20
N_REPEATS = 10
RANDOM_SEED = 42

CLASS_NAMES = [
    "buyer",
    "seller",
    "renter",
    "media outreach",
    "realtor network",
    "other",
]
METRIC_NAMES = ["precision", "recall", "f1", "specificity", "auc"]

# Assignment 9 item_id -> Module 10 item_id. Checked by statement overlap below.
MATCHED_ITEM_IDS = {
    "V1": "V2",
    "V3": "V5",
    "V6": "V12",
    "V7": "V21",
    "V8": "V24",
    "V9": "V13",
    "V11": "V4",
    "V16": "V15",
    "V17": "V23",
    "V20": "V18",
    "V21": "V8",
    "V22": "V9",
    "V23": "V7",
    "V27": "V19",
    "V28": "V3",
    "V30": "V1",
}

ROOT = Path(__file__).resolve().parents[1]
MODULE_9 = ROOT / "Module_9_assignment"
MODULE_10 = Path(__file__).resolve().parent
OUTPUT_DIR = MODULE_10 / "outputs"


def normalize_label(raw_label):
    if raw_label is None or (isinstance(raw_label, float) and np.isnan(raw_label)):
        return ""
    text = str(raw_label).strip()
    if text == "" or text.lower() == "nan":
        return ""
    return " ".join(text.lower().split())


def content_tokens(text):
    lowered = str(text).lower()
    lowered = re.sub(r"\([^)]*\)", " ", lowered)
    lowered = re.sub(r"\[[^\]]*\]", " ", lowered)
    lowered = re.sub(r"x{2,}", " ", lowered)
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return [token for token in lowered.split() if len(token) > 1]


def token_overlap(left_text, right_text):
    left_tokens = set(content_tokens(left_text))
    right_tokens = set(content_tokens(right_text))
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def make_pipeline():
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 1),
                    min_df=1,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=1.0,
                    class_weight="balanced",
                    solver="lbfgs",
                    max_iter=1000,
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )


def train_test_positions(row_count, train_size, split_seed):
    generator = np.random.RandomState(split_seed)
    positions = generator.permutation(row_count)
    train_positions = positions[:train_size]
    test_positions = positions[train_size:]
    return train_positions, test_positions


def class_probabilities(pipeline, statements, class_names):
    # Classes absent from the training rows have no coefficient. Their score stays 0.
    raw_probabilities = pipeline.predict_proba(statements)
    trained_names = list(pipeline.named_steps["classifier"].classes_)
    aligned = np.zeros((len(statements), len(class_names)), dtype=float)
    for column_index, class_name in enumerate(trained_names):
        aligned[:, class_names.index(class_name)] = raw_probabilities[:, column_index]
    return aligned


def safe_divide(numerator, denominator):
    if denominator == 0:
        return np.nan
    return numerator / denominator


def f1_from_precision_recall(precision, recall):
    if np.isnan(precision) or np.isnan(recall):
        return np.nan
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def one_vs_rest_counts(true_labels, predicted_labels, positive_name):
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    for true_label, predicted_label in zip(true_labels, predicted_labels):
        actual_positive = true_label == positive_name
        predicted_positive = predicted_label == positive_name
        if actual_positive and predicted_positive:
            true_positive += 1
        elif actual_positive and not predicted_positive:
            false_negative += 1
        elif (not actual_positive) and predicted_positive:
            false_positive += 1
        else:
            true_negative += 1
    return true_positive, false_positive, true_negative, false_negative


def one_vs_rest_auc(true_labels, positive_scores, positive_name):
    binary_truth = np.asarray(
        [1 if label == positive_name else 0 for label in true_labels],
        dtype=int,
    )
    positive_count = int(binary_truth.sum())
    if positive_count == 0 or positive_count == len(binary_truth):
        return np.nan
    return float(roc_auc_score(binary_truth, positive_scores))


def macro_average(values):
    numeric_values = np.asarray(values, dtype=float)
    defined_values = numeric_values[~np.isnan(numeric_values)]
    if defined_values.size == 0:
        return np.nan
    return float(defined_values.mean())


def probability_column(class_name):
    return "probability_" + class_name.replace(" ", "_")


def join_names(names):
    if len(names) == 0:
        return "(none)"
    return ", ".join(names)


def score_repeat(
    repeat_number,
    split_seed,
    statements,
    train_labels,
    reference_labels,
    item_ids,
    statement_text,
):
    train_positions, test_positions = train_test_positions(len(statements), TRAIN_SIZE, split_seed)
    pipeline = make_pipeline()
    pipeline.fit(statements[train_positions], train_labels[train_positions])

    actual_labels = reference_labels[test_positions]
    predicted_labels = pipeline.predict(statements[test_positions])
    probabilities = class_probabilities(pipeline, statements[test_positions], CLASS_NAMES)
    trained_classes = set(pipeline.named_steps["classifier"].classes_)

    class_rows = []
    for class_index, class_name in enumerate(CLASS_NAMES):
        true_positive, false_positive, true_negative, false_negative = one_vs_rest_counts(
            actual_labels,
            predicted_labels,
            class_name,
        )
        precision = safe_divide(true_positive, true_positive + false_positive)
        recall = safe_divide(true_positive, true_positive + false_negative)
        class_rows.append({
            "repeat": repeat_number,
            "split_seed": split_seed,
            "class_name": class_name,
            "precision": precision,
            "recall": recall,
            "f1": f1_from_precision_recall(precision, recall),
            "specificity": safe_divide(true_negative, true_negative + false_positive),
            "auc": one_vs_rest_auc(actual_labels, probabilities[:, class_index], class_name),
            "test_support": int(np.sum(actual_labels == class_name)),
            "train_support": int(np.sum(train_labels[train_positions] == class_name)),
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
        })

    prediction_rows = []
    for row_index, position in enumerate(test_positions):
        prediction_row = {
            "repeat": repeat_number,
            "split_seed": split_seed,
            "item_id": item_ids[position],
            "visitor_statement": statement_text[position],
            "train_label": train_labels[position],
            "actual_label": actual_labels[row_index],
            "predicted_label": predicted_labels[row_index],
            "correct": actual_labels[row_index] == predicted_labels[row_index],
        }
        for class_index, class_name in enumerate(CLASS_NAMES):
            prediction_row[probability_column(class_name)] = float(probabilities[row_index, class_index])
        prediction_rows.append(prediction_row)

    confusion_counts = confusion_matrix(actual_labels, predicted_labels, labels=CLASS_NAMES)
    summary = {
        "repeat": repeat_number,
        "split_seed": split_seed,
        "accuracy": float(np.mean(actual_labels == predicted_labels)),
        "macro_precision": macro_average([row["precision"] for row in class_rows]),
        "macro_recall": macro_average([row["recall"] for row in class_rows]),
        "macro_f1": macro_average([row["f1"] for row in class_rows]),
        "macro_specificity": macro_average([row["specificity"] for row in class_rows]),
        "macro_auc": macro_average([row["auc"] for row in class_rows]),
        "precision_classes_counted": int(np.sum(~np.isnan([row["precision"] for row in class_rows]))),
        "recall_classes_counted": int(np.sum(~np.isnan([row["recall"] for row in class_rows]))),
        "f1_classes_counted": int(np.sum(~np.isnan([row["f1"] for row in class_rows]))),
        "specificity_classes_counted": int(np.sum(~np.isnan([row["specificity"] for row in class_rows]))),
        "auc_classes_counted": int(np.sum(~np.isnan([row["auc"] for row in class_rows]))),
        "classes_missing_from_train": join_names(
            [class_name for class_name in CLASS_NAMES if class_name not in trained_classes]
        ),
        "classes_missing_from_test": join_names(
            [row["class_name"] for row in class_rows if row["test_support"] == 0]
        ),
        "train_item_ids": [str(item_ids[position]) for position in train_positions],
        "test_item_ids": [str(item_ids[position]) for position in test_positions],
    }
    return class_rows, summary, prediction_rows, confusion_counts


def run_experiment(statements, train_labels, reference_labels, item_ids, statement_text):
    class_rows = []
    repeat_rows = []
    prediction_rows = []
    summed_confusion = np.zeros((len(CLASS_NAMES), len(CLASS_NAMES)), dtype=int)
    for repeat_index in range(N_REPEATS):
        repeat_number = repeat_index + 1
        split_seed = RANDOM_SEED + repeat_index
        repeat_class_rows, summary, repeat_predictions, confusion_counts = score_repeat(
            repeat_number,
            split_seed,
            statements,
            train_labels,
            reference_labels,
            item_ids,
            statement_text,
        )
        class_rows.extend(repeat_class_rows)
        prediction_rows.extend(repeat_predictions)
        summed_confusion = summed_confusion + confusion_counts
        saved_summary = {
            key: value
            for key, value in summary.items()
            if key not in ("train_item_ids", "test_item_ids")
        }
        repeat_rows.append(saved_summary)

    class_metrics = pd.DataFrame(class_rows)
    repeat_summary = pd.DataFrame(repeat_rows)
    predictions = pd.DataFrame(prediction_rows)
    summary_rows = []
    for class_name in CLASS_NAMES:
        class_frame = class_metrics.loc[class_metrics["class_name"] == class_name]
        summary_row = {
            "class_name": class_name,
            "test_support_total": int(class_frame["test_support"].sum()),
            "train_support_total": int(class_frame["train_support"].sum()),
        }
        for metric_name in METRIC_NAMES:
            defined_values = class_frame[metric_name].dropna()
            summary_row[metric_name + "_mean"] = macro_average(class_frame[metric_name].to_numpy())
            if len(defined_values) < 2:
                summary_row[metric_name + "_std"] = np.nan
            else:
                summary_row[metric_name + "_std"] = float(defined_values.std(ddof=1))
            summary_row[metric_name + "_defined_runs"] = int(defined_values.shape[0])
        summary_rows.append(summary_row)
    class_summary = pd.DataFrame(summary_rows)
    return class_summary, repeat_summary, predictions, summed_confusion


def build_label_table(original, revised_source):
    revised_by_id = revised_source.set_index("item_id")
    rows = []
    revised_labels = []
    for _, original_row in original.iterrows():
        item_id = str(original_row["item_id"])
        original_label = normalize_label(original_row["expand_other"])
        module_10_id = MATCHED_ITEM_IDS.get(item_id)
        if module_10_id is None:
            rows.append({
                "item_id": item_id,
                "module_10_item_id": "",
                "in_module_10_form": False,
                "original_label": original_label,
                "revised_label": original_label,
                "label_changed": False,
                "adjudicated": "",
                "module_10_votes": "",
                "overlap": "",
                "note": "Not in the Module 10 form. Assignment 9 expand_other label retained.",
            })
            revised_labels.append(original_label)
            continue

        revised_row = revised_by_id.loc[module_10_id]
        overlap = token_overlap(original_row["visitor_statement"], revised_row["visitor_statement"])
        if overlap < 0.9:
            raise ValueError(
                f"{item_id} does not match Module 10 {module_10_id} (overlap {overlap:.3f})."
            )
        votes = [
            normalize_label(revised_row["annotator_1"]),
            normalize_label(revised_row["annotator_2"]),
            normalize_label(revised_row["annotator_3"]),
            normalize_label(revised_row["annotator_4"]),
        ]
        majority_label = normalize_label(revised_row["final_label"])
        if majority_label == "":
            applied_label = original_label
            changed = False
            note = "Module 10 final label is blank (no majority). Assignment 9 label retained."
        else:
            applied_label = majority_label
            changed = applied_label != original_label
            note = "Majority label replaced expand_other." if changed else "Majority label matches expand_other."
        rows.append({
            "item_id": item_id,
            "module_10_item_id": module_10_id,
            "in_module_10_form": True,
            "original_label": original_label,
            "revised_label": applied_label,
            "label_changed": changed,
            "adjudicated": revised_row["adjudicated"],
            "module_10_votes": " | ".join(votes),
            "overlap": round(overlap, 3),
            "note": note,
        })
        revised_labels.append(applied_label)

    matched_module_10_ids = set(MATCHED_ITEM_IDS.values())
    for module_10_id, revised_row in revised_by_id.iterrows():
        if module_10_id in matched_module_10_ids:
            continue
        stored_label = normalize_label(revised_row["final_label"])
        adjudicated = str(revised_row["adjudicated"]).strip().lower() == "yes"
        if adjudicated:
            exclusion_note = (
                "Tied votes, marked adjudicated. The stored final label was not used. "
                "This message is not in the Assignment 9 set, so it was not added."
            )
        else:
            exclusion_note = "Module 10 message is not in the Assignment 9 set, so it was not added."
        rows.append({
            "item_id": "",
            "module_10_item_id": module_10_id,
            "in_module_10_form": True,
            "original_label": "",
            "revised_label": "" if adjudicated else stored_label,
            "label_changed": False,
            "adjudicated": revised_row["adjudicated"],
            "module_10_votes": " | ".join(
                normalize_label(revised_row[column])
                for column in ("annotator_1", "annotator_2", "annotator_3", "annotator_4")
            ),
            "overlap": "",
            "note": exclusion_note,
        })
    return pd.DataFrame(rows), np.asarray(revised_labels)


def save_experiment(folder_name, class_summary, repeat_summary, predictions, summed_confusion):
    folder = OUTPUT_DIR / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    class_summary.to_csv(folder / "class_metrics_summary.csv", index=False)
    repeat_summary.to_csv(folder / "repeat_summary.csv", index=False)
    predictions.to_csv(folder / "test_predictions.csv", index=False)
    confusion_frame = pd.DataFrame(summed_confusion, index=CLASS_NAMES, columns=CLASS_NAMES)
    confusion_frame.index.name = "actual_label"
    confusion_frame.to_csv(folder / "confusion_matrix_sum.csv")
    return confusion_frame


def metric_value(class_summary, class_name, column_name):
    matching = class_summary.loc[class_summary["class_name"] == class_name, column_name]
    if len(matching) == 0 or pd.isna(matching.iloc[0]):
        return np.nan
    return float(matching.iloc[0])


def mean_of_column(repeat_summary, column_name):
    return float(repeat_summary[column_name].mean())


def format_number(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.3f}"


def comparison_row(class_name, experiments):
    row = {"class_name": class_name}
    for experiment_name, class_summary in experiments:
        for metric_name in METRIC_NAMES:
            row[f"{experiment_name}_{metric_name}"] = metric_value(
                class_summary, class_name, metric_name + "_mean"
            )
            row[f"{experiment_name}_{metric_name}_defined_runs"] = metric_value(
                class_summary, class_name, metric_name + "_defined_runs"
            )
    return row


def assert_splits_match_assignment_9(item_ids):
    saved_settings = json.loads((MODULE_9 / "outputs" / "run_settings.json").read_text(encoding="utf-8"))
    for repeat_index, saved_split in enumerate(saved_settings["splits"]):
        split_seed = RANDOM_SEED + repeat_index
        train_positions, test_positions = train_test_positions(len(item_ids), TRAIN_SIZE, split_seed)
        train_ids = [str(item_ids[position]) for position in train_positions]
        test_ids = [str(item_ids[position]) for position in test_positions]
        if train_ids != saved_split["train_item_ids"] or test_ids != saved_split["test_item_ids"]:
            raise ValueError(f"Repeat {repeat_index + 1} split does not match Assignment 9.")


def assert_baseline_matches_saved(class_summary):
    saved = pd.read_csv(MODULE_9 / "outputs" / "class_metrics_summary.csv")
    mismatches = []
    for metric_name in METRIC_NAMES:
        column_name = metric_name + "_mean"
        for class_name in CLASS_NAMES:
            fresh = metric_value(class_summary, class_name, column_name)
            saved_match = saved.loc[saved["class_name"] == class_name, column_name]
            saved_value = float(saved_match.iloc[0]) if len(saved_match) and pd.notna(saved_match.iloc[0]) else np.nan
            if np.isnan(fresh) and np.isnan(saved_value):
                continue
            if np.isnan(fresh) or np.isnan(saved_value) or abs(fresh - saved_value) > 1e-9:
                mismatches.append((class_name, column_name, saved_value, fresh))
    return mismatches


def main():
    original = pd.read_csv(MODULE_9 / "labeled_visitor_intent.csv")
    revised_source = pd.read_csv(MODULE_10 / "labeled_visitor_intent.csv")
    label_table, revised_labels = build_label_table(original, revised_source)
    original_labels = original["expand_other"].map(normalize_label).to_numpy()
    unknown = sorted((set(original_labels) | set(revised_labels)) - set(CLASS_NAMES))
    if unknown:
        raise ValueError("Unexpected labels: " + ", ".join(unknown))

    statements = original["visitor_statement"].astype(str).to_numpy()
    item_ids = original["item_id"].astype(str).to_numpy()
    assert_splits_match_assignment_9(item_ids)

    experiments = {
        "baseline_on_original_labels": run_experiment(
            statements, original_labels, original_labels, item_ids, statements
        ),
        "revised_on_original_labels": run_experiment(
            statements, revised_labels, original_labels, item_ids, statements
        ),
        "baseline_on_revised_labels": run_experiment(
            statements, original_labels, revised_labels, item_ids, statements
        ),
        "revised_on_revised_labels": run_experiment(
            statements, revised_labels, revised_labels, item_ids, statements
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    label_table.to_csv(OUTPUT_DIR / "label_changes.csv", index=False)
    for folder_name, (class_summary, repeat_summary, predictions, summed_confusion) in experiments.items():
        save_experiment(folder_name, class_summary, repeat_summary, predictions, summed_confusion)

    baseline_summary = experiments["baseline_on_original_labels"][0]
    mismatches = assert_baseline_matches_saved(baseline_summary)

    comparison_rows = [comparison_row(class_name, [(name, result[0]) for name, result in experiments.items()]) for class_name in CLASS_NAMES]
    comparison = pd.DataFrame(comparison_rows)
    macro_row = {"class_name": "macro_mean_of_repeats"}
    for experiment_name, (_, repeat_summary, _, _) in experiments.items():
        for metric_name in ("accuracy", "macro_precision", "macro_recall", "macro_f1", "macro_specificity", "macro_auc"):
            macro_row[f"{experiment_name}_{metric_name}"] = mean_of_column(repeat_summary, metric_name)
    pd.concat([comparison, pd.DataFrame([macro_row])], ignore_index=True).to_csv(
        OUTPUT_DIR / "comparison_metrics.csv", index=False
    )

    changed_ids = label_table.loc[label_table["label_changed"] == True, "item_id"].tolist()
    focus_frames = []
    for experiment_name, (_, _, predictions, _) in experiments.items():
        focus = predictions.loc[predictions["item_id"].isin(changed_ids), [
            "repeat", "item_id", "actual_label", "predicted_label", "correct",
        ]].copy()
        focus.insert(0, "experiment", experiment_name)
        focus_frames.append(focus)
    pd.concat(focus_frames, ignore_index=True).to_csv(OUTPUT_DIR / "changed_item_predictions.csv", index=False)

    settings = {
        "source_records": "Module_9_assignment/labeled_visitor_intent.csv",
        "revised_labels": "Module_10_assignment/labeled_visitor_intent.csv final_label, matched by statement",
        "records_retained_unchanged": int((label_table["item_id"] != "").sum() - label_table["label_changed"].sum()),
        "records_relabeled": changed_ids,
        "module_10_messages_not_added": label_table.loc[label_table["item_id"] == "", "module_10_item_id"].tolist(),
        "same_reference_comparison": "revised_on_original_labels uses revised training labels and Assignment 9 test labels",
        "revised_reference_comparison": "baseline_on_revised_labels and revised_on_revised_labels score the same test rows against the revised labels",
        "modeling_change": "score_repeat takes separate train and reference labels. Fitting, features, hyperparameters, splits, and metric formulas are unchanged.",
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "assignment_9_sklearn_version": "1.9.1",
        "baseline_matches_saved_assignment_9": len(mismatches) == 0,
        "baseline_mismatches": [
            {"class_name": class_name, "metric": metric_name, "saved": saved_value, "rerun": fresh}
            for class_name, metric_name, saved_value, fresh in mismatches
        ],
    }
    (OUTPUT_DIR / "run_settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")

    print("sklearn", sklearn.__version__, "numpy", np.__version__)
    print("baseline mismatches vs saved Assignment 9:", len(mismatches))
    for class_name, metric_name, saved_value, fresh in mismatches:
        print(f"  {class_name} {metric_name}: saved {saved_value} rerun {fresh}")
    print("changed labels:")
    print(label_table.loc[label_table["label_changed"] == True, [
        "item_id", "module_10_item_id", "original_label", "revised_label", "module_10_votes"
    ]].to_string(index=False))
    print("\nMean across repeats")
    for experiment_name, (_, repeat_summary, _, summed_confusion) in experiments.items():
        print(
            experiment_name,
            "acc", format_number(mean_of_column(repeat_summary, "accuracy")),
            "P", format_number(mean_of_column(repeat_summary, "macro_precision")),
            "R", format_number(mean_of_column(repeat_summary, "macro_recall")),
            "F1", format_number(mean_of_column(repeat_summary, "macro_f1")),
            "spec", format_number(mean_of_column(repeat_summary, "macro_specificity")),
            "auc", format_number(mean_of_column(repeat_summary, "macro_auc")),
            "f1_classes", format_number(mean_of_column(repeat_summary, "f1_classes_counted")),
        )
        print(pd.DataFrame(summed_confusion, index=CLASS_NAMES, columns=CLASS_NAMES).to_string())
        print()


if __name__ == "__main__":
    main()
