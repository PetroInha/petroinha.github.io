import time
import subprocess
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def run_tasks():
    while True:
        try:
            subprocess.run(["python", "_script/gather_energy_stats.py"], check=True)
            subprocess.run(["python", "_script/git_push_energy_stats.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Script failed with exit code {e.returncode}. Retrying in 5 seconds...")
            time.sleep(5)
        else:
            print("Tasks completed successfully.")
            break

def get_seconds_until_230_pm_texas():
    # Note: Most of Texas is in the Central timezone. 
    # If you are in El Paso, use "America/Denver" instead.
    texas_tz = ZoneInfo("America/Chicago")
    now = datetime.now(texas_tz)
    
    # Set target to 14:30 (2:30 PM) today
    target = now.replace(hour=14, minute=30, second=0, microsecond=0)
    
    # If it is already past 2:30 PM today, set the target for tomorrow
    if now >= target:
        target += timedelta(days=1)
        
    return (target - now).total_seconds()

if __name__ == "__main__":
    print("Starting scheduler...")
    while True:
        wait_seconds = get_seconds_until_230_pm_texas() + 60  # Add an extra minute to ensure we are past 2:30 PM
        print(f"Sleeping for {wait_seconds / 3600:.2f} hours until 2:30 PM Texas time.")
        time.sleep(wait_seconds)
        
        # It's time! Run the tasks
        run_tasks()