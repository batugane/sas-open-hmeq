import yaml
import argparse
import logging

from src.data_loading    import load_data
from src.preprocessing  import split_and_impute
from src.training       import train_gbc
from src.evaluation     import evaluate
from src.serialization  import serialize_model
from src.import_model   import import_to_model_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(skip_import: bool):
    # 1. load config
    cfg = yaml.safe_load(open("config/params.yaml"))

    # 2. data
    df = load_data(cfg["data"]["path"])
    preds = ["LOAN","MORTDUE","VALUE","YOJ","DEROG","DELINQ","CLAGE","NINQ","CLNO","DEBTINC"]
    x_train, x_test, y_train, y_test = split_and_impute(
        df, preds, "BAD",
        cfg["preprocessing"]["test_size"],
        cfg["preprocessing"]["random_state"]
    )

    # 3. train
    model = train_gbc(x_train, y_train, cfg["model"]["params"])

    # 4. evaluate
    y_pred, y_proba = evaluate(model, x_test, y_test)

    # 5. serialize
    serialize_model(
        model,
        preds,
        df,
        cfg["serialization"]["output_dir"],
        cfg["model"]["type"]
    )

    # 6. (optionally) import
    if skip_import:
        logger.info("ℹ️  Dry run: skipping SAS Model Manager import")
    else:
        import_to_model_manager(
            input_data=df[preds],
            model_prefix=cfg["model"]["type"],
            project="HMEQModelsBD",
            serialization_path=cfg["serialization"]["output_dir"],
            predict_method=[model.predict_proba, [int, int]],
            score_metrics=["EM_CLASSIFICATION","EM_EVENTPROBABILITY"],
            missing_values=True,
            host=cfg["pzmm"]["host"],
            protocol=cfg["pzmm"]["protocol"]
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Run everything up through serialization, but skip the SAS import step"
    )
    args = parser.parse_args()
    main(skip_import=args.skip_import)
