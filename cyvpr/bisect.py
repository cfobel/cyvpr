import sys


class BisectBase(object):
    def _starting_bad(self):
        raise NotImplementedError

    def _starting_good(self):
        raise NotImplementedError

    def evaluate(self, value):
        raise NotImplementedError

    def _next_after_good(self, value):
        raise NotImplementedError

    def _next_after_bad(self, value):
        raise NotImplementedError

    def _reset(self, max_iterations):
        self.bad = self._starting_bad()
        self.good = self._starting_good()
        self.max_iterations = max_iterations
        self._iteration = 0

    def _run(self, start_value):
        self._iteration += 1
        if self._iteration >= self.max_iterations:
            raise IndexError, ('Maximum number of iterations (%d) reached.' %
                               self._iteration)
        if (self.bad is not None and self.bad == start_value):
            # We have arrived back at the most-recently-failed value, so it's
            # time to stop, returning the lowest-successful value we found
            # along the way.
            return self.good
        good = self.evaluate(start_value)
        if not good:
            self.bad = start_value
            return self._run(self._next_after_bad(start_value))
        else:
            self.good = start_value
            return self._run(self._next_after_good(start_value))

    def start(self, start_value, max_iterations=10):
        self._iteration = 0
        self._reset(max_iterations)
        return self._run(start_value)


class BinaryLeftBisect(BisectBase):
    def __init__(self, lower_bound=0):
        self.lower_bound = lower_bound

    def evaluate(self, value):
        raise NotImplementedError

    def _starting_bad(self):
        return self.lower_bound

    def _starting_good(self):
        return sys.maxint

    def _next_after_good(self, value):
        # Since the current run was successful, try to find a lower successful
        # value between the current value and the most-recently-failed value.
        return (self.good - self.bad) / 2 + self.bad

    def _next_after_bad(self, value):
        if self.good == sys.maxint:
            # We haven't processed a successful evaluation yet, so double
            # the start-value and try again.
            return value * 2
        else:
            # There has been at least one value that has resulted in a
            # successful evaluation.  Since the current value failed
            # evaluation, try a value half-way between the current value
            # and the lowest successful value encountered so far.
            return self._next_after_good(value)


class BinaryRightBisect(BisectBase):
    def __init__(self, upper_bound=sys.maxint):
        self.upper_bound = upper_bound

    def evaluate(self, value):
        raise NotImplementedError

    def _starting_bad(self):
        return self.upper_bound

    def _starting_good(self):
        return 0

    def _next_after_good(self, value):
        # Since the current run was successful, try to find a higher successful
        # value between the current value and the most-recently-failed value.
        next_value = max((self.bad - self.good) / 2, 1) + self.good
        return next_value

    def _next_after_bad(self, value):
        if self.good == 0:
            # We haven't processed a successful evaluation yet, so double
            # the start-value and try again.
            next_value = value / 2
        else:
            # There has been at least one value that has resulted in a
            # successful evaluation.  Since the current value failed
            # evaluation, try a value half-way between the current value
            # and the lowest successful value encountered so far.
            next_value = self._next_after_good(value)
        return next_value


class BisectLowerBound(BinaryLeftBisect):
    def __init__(self, target_lower_bound, lower_bound=0):
        self.target_lower_bound = target_lower_bound
        super(BisectLowerBound, self).__init__(lower_bound)

    def evaluate(self, value):
        result = (value >= self.target_lower_bound)
        return result


class BisectUpperBound(BinaryRightBisect):
    def __init__(self, target_upper_bound, upper_bound=sys.maxint):
        self.target_upper_bound = target_upper_bound
        super(BisectUpperBound, self).__init__(upper_bound)

    def evaluate(self, value):
        result = (value <= self.target_upper_bound)
        return result
