from apscheduler.schedulers.blocking import BlockingScheduler
from bot_coordination import run_all_bots

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour='9', minute='58', timezone='America/New_York')
def run():
	print('starting job')
	run_all_bots()

sched.start()