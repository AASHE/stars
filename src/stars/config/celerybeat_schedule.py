from celery.schedules import crontab


STARS_TASK_SCHEDULE = {

    # Executes every morning at 6:15 A.M
    # stars.apps.institutions.tasks.monitor_subscription
    'monitor subscriptions every morning': {
        'task': 'institutions.monitor_subscription',
        'schedule': crontab(hour=6, minute=15),
    },
    # Executes every morning at 2am
    # stars.apps.submissions.tasks.load_subcategory_quartiles
    'load SubcategoryQuartiles table every morning': {
        'task': 'submissions.load_subcategory_quartiles',
        'schedule': crontab(hour=2, minute=0)
    },
    # Executes every morning at 3am
    # stars.apps.institutions.tasks.update_from_iss
    'update iss values every morning': {
        'task': 'institutions.update_from_iss',
        'schedule': crontab(hour=3, minute=0),
    },
    # Executes once a month
    # stars.config.celery.run_cleanup
    'clear expired sessions on the first of every month': {
        'task': 'tasks.run_cleanup',
        'schedule': crontab(0, 0, day_of_month='1'),
    },
    # Executes every morning at 5am
    # stars.apps.tasks.tasks.send_notifications
    'send out notifications when necessary': {
        'task': 'tasks.send_notifications',
        'schedule': crontab(hour=7, minute=0),
    },
    # Executes every morning at 5am
    # stars.apps.institutions.tasks.email_expiring_ratings
    'send out email of expiring ratings': {
        'task': 'institutions.email_expiring_ratings',
        'schedule': crontab(hour=5, minute=0),
    },
}
