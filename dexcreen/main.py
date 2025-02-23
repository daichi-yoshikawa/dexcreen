import os
import logging
import threading

from dotenv import load_dotenv

from dexcreen import Dexcreen
from logger_setup import configure_logger


load_dotenv()

configure_logger()
logger = logging.getLogger(__name__)

lock = threading.Lock()
dexcreen = Dexcreen()
 
def fetch_cgm_data(stop_event):
  while not stop_event.is_set():
    with lock:
      try:
        dexcreen.fetch_cgm_data()
        interval = dexcreen.get_interval()
        logger.info(f'Fetch next data {interval} sec later.')
      except Exception:
        stop_event.set()
    woke_up_early = stop_event.wait(timeout=interval)
    if woke_up_early:
      break


def refresh_screen_letters(stop_event):
  while not stop_event.is_set():
    with lock:
      try:
        dexcreen.display_letters()
      except Exception:
        stop_event.set()
    woke_up_early = stop_event.wait(timeout=3)
    if woke_up_early:
      break


def refresh_screen_chart(stop_event):
  while not stop_event.is_set():
    with lock:
      try:
        dexcreen.display_chart()
      except Exception:
        stop_event.set()
    woke_up_early = stop_event.wait(timeout=10)
    if woke_up_early:
      break


def worker():
  logger.info('worker is called.')
  dexcreen = Dexcreen()

  while True:
    try:
      dexcreen.run()
      dexcreen.sleep()
    except KeyboardInterrupt as e:
      logger.info('ctrl + c')
      dexcreen.cleanup()
      logger.info('Shutdown app in worker...')
      exit()
    except Exception as e:
      logger.error(e)
      dexcreen.cleanup()
      logger.info('Shutdown app in worker...')
      exit()


if __name__ == "__main__":
  dexcreen.init()

  stop_event = threading.Event()
  threads = [
    threading.Thread(target=fetch_cgm_data, args=(stop_event,)),
    threading.Thread(target=refresh_screen_letters, args=(stop_event,)),
    threading.Thread(target=refresh_screen_chart, args=(stop_event,)),
  ]

  for thread in threads:
    thread.start()

  try:
    for thread in threads:
      thread.join()
  except KeyboardInterrupt:
    logger.info('KeyboardInterrupt detected.')
    stop_event.set()
    for thread in threads:
      thread.join()
    logger.info('All threads stopped due to KeyboardInterrupt.')
  except Exception as e:
    logger.error('Exception in one of the threads: {e}')
    stop_event.set()
    for thread in threads:
      thread.join()
    logger.error('All threads stopped due to Exception.')
  else:
    logger.info('All threads stopped without error')
