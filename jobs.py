from apscheduler.schedulers.blocking import BlockingScheduler
from bot_coordination import run_all_bots

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour='2', minute='1', timezone='America/New_York')
def run():
 	run_all_bots()

sched.start()