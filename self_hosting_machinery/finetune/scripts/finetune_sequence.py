import os
import signal
import subprocess
import sys
import time

import psutil


def catch_sigusr1(signum, frame):
    print("catched SIGUSR1")
    current_process = psutil.Process()
    for child in current_process.children(recursive=False):
        os.kill(child.pid, signal.SIGUSR1)


if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, catch_sigusr1)

    filter_only = ("--filter-only" in sys.argv)
    if not filter_only:
        os.environ["LORA_LOGDIR"] = time.strftime("lora-%Y%m%d-%H%M%S")
    else:
        os.environ["LORA_LOGDIR"] = "NO_LOGS"
    try:
        subprocess.check_call([sys.executable, "-m", "self_hosting_machinery.finetune.scripts.process_uploaded_files"])
        subprocess.check_call([sys.executable, "-m", "self_hosting_machinery.finetune.scripts.finetune_filter"])
        if not filter_only:
            subprocess.check_call([sys.executable, "-m", "self_hosting_machinery.finetune.scripts.finetune_train"])
    except subprocess.CalledProcessError as e:
        print(f"finetune_sequence: {e}")
        sys.exit(1)
