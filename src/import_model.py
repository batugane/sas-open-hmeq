import getpass
from sasctl import Session
import sasctl.pzmm as pzmm

def import_to_model_manager(
    input_data, model_prefix, project, serialization_path,
    predict_method, score_metrics, missing_values,
    host, protocol
):
    username = getpass.getpass("SAS username: ")
    password = getpass.getpass("SAS password: ")
    sess = Session(host, username, password, protocol=protocol)
    # zip & import
    pzmm.ImportModel.import_model(
        model_files=serialization_path,
        model_prefix=model_prefix,
        project=project,
        input_data=input_data,
        predict_method=predict_method,
        score_metrics=score_metrics,
        overwrite_model=True,
        target_values=["0","1"],
        target_index=1,
        model_file_name=model_prefix + ".pickle",
        missing_values=missing_values
    )
