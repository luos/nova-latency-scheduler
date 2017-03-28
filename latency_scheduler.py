from nova.scheduler import driver, filter_scheduler


class LatencyAwareScheduler(filter_scheduler.FilterScheduler):
    def hosts_up(self, context, topic):
        return super(LatencyAwareScheduler, self).hosts_up(context, topic)

    def select_destinations(self, context, spec_obj):
        return super(LatencyAwareScheduler, self).select_destinations(context, spec_obj)

    def run_periodic_tasks(self, context):
        super(LatencyAwareScheduler, self).run_periodic_tasks(context)