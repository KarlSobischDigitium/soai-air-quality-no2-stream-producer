import logging
import logging.config
from pathlib import Path
import os


####### SET UP PROJECT PATH #######
os.environ['SOAI'] = str(Path(__file__).parent / "..")
if os.path.exists(os.environ.get("SOAI") + "/logs") is False:
    os.mkdir(os.environ.get("SOAI") + "/logs")

####### SET UP LOGGER #######
# Open the config file and save a temporary copy with the correct path
file_in = Path(os.environ.get("SOAI") + "/configs/logging.conf")
file_out = Path(os.environ.get("SOAI") + "/configs/loggingTEMP.conf")
with open(file_in, "rt") as fin:
    with open(file_out, "wt") as fout:
        for line in fin:
            if os.name == "nt":
                fout.write(line.replace('PATH_TO_PROJECT', os.environ.get("SOAI").replace("\\", "\\\\")  ))
            else:
                fout.write(line.replace('PATH_TO_PROJECT', os.environ.get("SOAI")))

# Parse the temporary file with the correct paths to the logging module
logging.config.fileConfig(file_out)
logger = logging.getLogger()

logger.info(f'Use {os.environ.get("SOAI")} as project path.')


# log if env vars are set.
if os.environ.get("SOAI_MODEL_PATH") is None:
    logger.warning("SOAI_MODEL_PATH not set")
else:
    logger.info(f'SOAI_MODEL_PATH env var is set to {os.environ.get("SOAI_MODEL_PATH")}')

if os.environ.get("SOAI") is None:
    logger.warning("SOAI env var  not set")
else:
    logger.info(f'SOAI env var is set to {os.environ.get("SOAI")}')
