import uuid
import datetime
import json
import os

class BaseAgent:
    def __init__(self, agent_name=None, context=None, task_id=None):
        self.agent_name = agent_name or self.__class__.__name__
        self.context = context or {}
        self.task_id = task_id or str(uuid.uuid4())
        self.state_file = f"agent_state_{self.agent_name}.json"

    def run(self, *args, **kwargs):
        raise NotImplementedError("Each agent must implement its own run() method.")

    def retry(self, func, max_retries=3, delay=2, *args, **kwargs):
        import time
        attempt = 0
        while attempt < max_retries:
            try:
                self.log_result(f"Attempt {attempt+1}/{max_retries} for {func.__name__}")
                return func(*args, **kwargs)
            except Exception as e:
                self.report_error(e)
                attempt += 1
                if attempt < max_retries:
                    time.sleep(delay)
        raise

    def checkpoint(self, state: dict = None):
        state = state or self.context
        checkpoint_file = self.state_file
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log_result(f"Checkpoint saved to {checkpoint_file}")
        except Exception as e:
            self.report_error(f"Failed to save checkpoint: {e}")

    def log_result(self, message, level="info"):
        ts = datetime.datetime.now().isoformat()
        log_dir = os.path.join("logs", "agent_logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{self.agent_name}_{ts[:10]}.log")
        with open(log_file, "a") as f:
            f.write(f"[{ts}] [{level.upper()}] [{self.task_id}] {message}\n")

    def report_error(self, error, context=None):
        ts = datetime.datetime.now().isoformat()
        log_dir = os.path.join("logs", "agent_logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{self.agent_name}_{ts[:10]}.log")
        with open(log_file, "a") as f:
            f.write(f"[{ts}] [ERROR] [{self.task_id}] {str(error)} | Context: {context or self.context}\n") 