import logging
from dotenv import load_dotenv
from .logger_setup import configure_logger

load_dotenv()
configure_logger()

import os
import queue
import threading

from dotenv import load_dotenv

from .dexcreen import Dexcreen


logger = logging.getLogger(__name__)

lock = threading.Lock()
dexcreen = Dexcreen()
 
def fetch_cgm_data(stop_event, exception_queue):
  while not stop_event.is_set():
    interval = 30
    with lock:
      try:
        dexcreen.fetch_cgm_data()
        interval = dexcreen.get_interval()
        logger.info(f'Fetch next data {interval} sec later.')
      except Exception as e:
        logger.error(f'Exception in fetch_cgm_data thread: {e}')
        exception_queue.put(e)
        stop_event.set()
    stop_event.wait(timeout=interval)


def refresh_screen(
    stop_event, exception_queue, timeout, chart_update_period):
  count = 0
  while not stop_event.is_set():
    with lock:
      try:
        count += 1
        update_chart = timeout * count >= chart_update_period
        dexcreen.refresh_display(update_chart=update_chart)
        count = 0 if update_chart else count

      except Exception as e:
        logger.error(f'Exception in refresh_screen_letters thread: {e}')
        exception_queue.put(e)
        stop_event.set()
    stop_event.wait(timeout=timeout)


def run_all_threads():
  dexcreen.init()

  stop_event = threading.Event()
  exception_queue = queue.Queue()

  threads = [
    threading.Thread(
      target=fetch_cgm_data, args=(stop_event, exception_queue)),
    threading.Thread(
      target=refresh_screen, args=(stop_event, exception_queue, 10, 180)),
  ]

  for thread in threads:
    thread.start()

  for thread in threads:
    thread.join()

  if not exception_queue.empty():
    raise exception_queue.get()


if __name__ == "__main__":
  keyboard_interrupt = False

  while True:
    try:
      run_all_threads()
    except KeyboardInterrupt:
      logger.info('KeyboardInterrupt detected.')
      keyboard_interrupt = True
    except Exception as e:
      logger.error('Exception is raised. Retry all threads.')
    finally:
      dexcreen.cleanup()
      if keyboard_interrupt:
        exit()
