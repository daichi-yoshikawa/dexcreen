from dotenv import load_dotenv
import os
import logging


def configure_logger():
  load_dotenv()

  log_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    os.getenv('LOGGER_FILE_PATH', ''))
  log_file_path = os.path.join(log_dir, os.getenv('LOGGER_FILE_NAME', ''))

  if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

  handlers = [logging.StreamHandler()]
  if log_file_path:
    handlers.append(logging.FileHandler(log_file_path))

  logging.basicConfig(
    level=os.getenv('LOGGER_LEVEL', 'INFO'),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=handlers)
