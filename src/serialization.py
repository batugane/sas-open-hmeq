from pathlib import Path
import sasctl.pzmm as pzmm
import pandas as pd

def serialize_model(model, predictor_cols, data_df, output_dir, prefix):
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    # 1. pickle
    pzmm.PickleModel.pickle_trained_model(prefix, model, path)
    # 2. JSON var mappings
    pzmm.JSONFiles.write_var_json(data_df[predictor_cols], True, path)
    output_var = pd.DataFrame(
        columns=["EM_CLASSIFICATION","EM_EVENTPROBABILITY"],
        data=[["A", 0.5]]
    )
    pzmm.JSONFiles.write_var_json(output_var, False, path)
    # 3. model properties & metadata
    pzmm.JSONFiles.write_model_properties_json(
        model_name=prefix,
        target_variable="BAD",
        target_values=["1","0"],
        json_path=path,
        model_desc=f"Description for the {prefix} model.",
        model_algorithm="GradientBoosting",
        modeler="sasdemo"
    )
    pzmm.JSONFiles.write_file_metadata_json(prefix, path)
