import sys


class BisectBase(object):
    def _reset(self, max_iterations):
        self.most_recent_failed = None
        self.lowest_success = sys.maxint
        self.max_iterations = max_iterations
        self._iteration = 0

    def _next_after_success(self, value):
        # Since the current run was successful, try to find a lower successful
        # value between the current value and the most-recently-failed value.
        return ((self.lowest_success - self.most_recent_failed) / 2 +
                self.most_recent_failed)

    def _next_after_failure(self, value):
        if self.lowest_success == sys.maxint:
            # We haven't processed a successful evaluation yet, so double
            # the start-value and try again.
            return value * 2
        else:
            # There has been at least one value that has resulted in a
            # successful evaluation.  Since the current value failed
            # evaluation, try a value half-way between the current value
            # and the lowest successful value encountered so far.
            return self._next_after_success(value)

    def _run(self, start_value):
        self._iteration += 1
        if self._iteration >= self.max_iterations:
            raise IndexError, ('Maximum number of iterations (%d) '
                               'reached.' % self._iteration)
        if (self.most_recent_failed is not None and
            self.most_recent_failed == start_value):
            # We have arrived back at the most-recently-failed value, so it's
            # time to stop, returning the lowest-successful value we found
            # along the way.
            return self.lowest_success
        success = self.evaluate(start_value)
        if not success:
            self.most_recent_failed = start_value
            return self._run(self._next_after_failure(start_value))
        else:
            self.lowest_success = start_value
            return self._run(self._next_after_success(start_value))

    def evaluate(self, value):
        raise NotImplementedError

    def start(self, start_value, max_iterations=10):
        self._iteration = 0
        self._reset(max_iterations)
        return self._run(start_value)
