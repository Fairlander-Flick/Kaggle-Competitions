import os
import subprocess
import time

kernel_slug = "fairlanderflick/neurogolf-400-tasks-auto-trainer"
comp_name = "neurogolf-2026"

def log_it(msg):
    with open("poll_log.txt", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    print(msg)

log_it("Starting polling for kernel: " + kernel_slug)

while True:
    status_out = subprocess.run(["kaggle", "kernels", "status", kernel_slug], capture_output=True, text=True)
    stdout_lower = status_out.stdout.lower()
    
    if "complete" in stdout_lower:
        log_it("Kernel completed! Downloading outputs...")
        os.makedirs("kaggle_logs", exist_ok=True)
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        subprocess.run(["kaggle", "kernels", "output", kernel_slug, "-p", "kaggle_logs"], env=env)
        
        zip_path = "kaggle_logs/submission.zip"
        if os.path.exists(zip_path):
            log_it("Found submission.zip. Submitting to Kaggle...")
            submit_out = subprocess.run(["kaggle", "competitions", "submit", "-c", comp_name, "-f", zip_path, "-m", "Auto-Trainer 400 Tasks Baseline"], capture_output=True, text=True)
            log_it("Submission output: " + submit_out.stdout)
            
            # Log to experiments
            with open("EXPERIMENTS.md", "a", encoding="utf-8") as f:
                f.write(f"\n| Auto-Trainer | submission.zip | {time.strftime('%Y-%m-%d')} | Submitted via background script | Pending |\n")
        else:
            log_it("No submission.zip found in output.")
        break
    elif "error" in stdout_lower:
        log_it("Kernel errored out. Downloading log...")
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        subprocess.run(["kaggle", "kernels", "output", kernel_slug, "-p", "kaggle_logs"], env=env)
        break
    else:
        time.sleep(60)
