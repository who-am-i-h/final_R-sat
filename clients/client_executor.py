import subprocess
import logging
import os
import time

logging.basicConfig(filename="client_executor.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def runner():
    while True:
        if "client_rsa.py" not in os.listdir() or "client_EC.py" not in os.listdir():
            return "No such file exists."
        if "client_rsa.py" in os.listdir():
            try:
                subprocess.run(["python", "client_rsa.py"], check=True)
            except subprocess.CalledProcessError as e:
                if e.returncode == 2:
                    logger.info(f"client stopped intentionlly exit-status{e.returncode}")
                    exit()
                logger.error(f"Error Ocurred -->{e}")
                time.sleep(5)
            except Exception as e:
                logger.error(e)
                time.sleep(5)
        else:
            try:
                subprocess.run(["python", "client_EC.py"], check=True)
            except subprocess.CalledProcessError as e:
                if e.returncode == 2:
                    logger.info(f"client stopped intentionlly exit-status{e.returncode}")
                    exit()
                logger.error(f"Error Ocurred -->{e}")
                time.sleep(5)
            except Exception as e:
                logger.error(e)
                time.sleep(5)
            
runner()





    