from apscheduler.schedulers.blocking import BlockingScheduler
from bot_coordination import run_all_bots

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour='23', minute='46', timezone='America/New_York')
def run():
 	run_all_bots()

sched.start()