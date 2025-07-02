import sasctl.pzmm as pzmm
from sasctl import Session
import logging

# Use our auth utilities for OAuth2 token handling
from src.utils.auth_utils import refresh_access_token, generate_access_token

logger = logging.getLogger(__name__)

def import_to_model_manager(
    input_data,
    model_prefix,
    project,
    serialization_path,
    predict_method,
    score_metrics,
    missing_values,
    host,
    protocol
):
    """
    Import a serialized model into SAS Model Manager using OAuth2 token-based authentication.
    """
    # Obtain an access token (refresh or generate)
    try:
        access_token = refresh_access_token()
        logger.info("✔ Access token refreshed.")
    except Exception as e:
        logger.warning("⚠️ Refresh failed; generating new access token. Error: %s", e)
        try:
            access_token = generate_access_token()
        except Exception as e2:
            logger.error("Failed to generate access token: %s", e2)
            raise
    # Create a session using the bearer token
    try:
        with Session(host, token=access_token, protocol=protocol) as sess:
            pzmm.ImportModel.import_model(
                model_files=serialization_path,
                model_prefix=model_prefix,
                project=project,
                input_data=input_data,
                predict_method=predict_method,
                score_metrics=score_metrics,
                overwrite_model=True,
                target_values=["0", "1"],
                target_index=1,
                model_file_name=f"{model_prefix}.pickle",
                missing_values=missing_values
            )
            logger.info("✅ Model '%s' imported into project '%s'.", model_prefix, project)
    except Exception as e:
        logger.error("Failed to import model: %s", e)
        raise
