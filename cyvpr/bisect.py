import sys


class BoundFinderBase(object):
    '''
    This class provides an API for finding a boundary-value for a monotonic
    function, _i.e., an upper-bound or lower-bound on a parameter that results
    in a successful evaluation of the user-defined `evaluate` method.

    By calling the `start` method with some initial value, several iterations
    of evaluation are performed to find the boundary value of interest.

    __NB__ This class is an abstract-base-class, since it does not provide a
    default implementation for the following methods:

      * `evaluate`
      * `_next_after_bad`
      * `_next_after_good`
    '''
    def evaluate(self, value):
        '''
        Return `True` to indicate success for the provided value, or `False` to
        indicate failure.  This result is used to guide the search to the
        boundary of interest.
        '''
        raise NotImplementedError

    def _next_after_bad(self, value):
        '''
        Given a value that failed evaluation, propose a new value to evaluate.
        '''
        raise NotImplementedError

    def _next_after_good(self, value):
        '''
        Given a value that resulted in a successful evaluation, propose a new
        value to evaluate to try to tighten the bound.
        '''
        raise NotImplementedError


    def __init__(self, known_bad, known_good, evaluate=None):
        if evaluate is not None:
            self.evaluate = evaluate
        self.known_bad = known_bad
        self.known_good = known_good

    def _starting_bad(self):
        return self.known_bad

    def _starting_good(self):
        return self.known_good

    def _reset(self, max_iterations):
        '''
        Reset the state of the finder to prepare for a new search.
        '''
        self.bad = self._starting_bad()
        self.good = self._starting_good()
        self.max_iterations = max_iterations
        self._iteration = 0
        self._good_found = False

    def _run(self, start_value):
        '''
        Perform a recursive search to find the boundary of interest, by
        successively evaluating potential values.  After each evaluation, the
        `_next_after_bad` and `_next_after_good` methods are used to determine
        the next value to try.

        __NB__ TODO: Look up terminology for recursive strategies in
        "Structured Parallel Programming".  They provide a term for what I call
        `exit` here.

        The recursive calls exit when the proposed test value is the same as
        the most-recently tested value that failed the evaluation.  In this
        case, we know that we have encountered the transition from `good` to
        `bad`, _i.e., we have found the boundary_.
        '''
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
            self._good_found = True
            self.good = start_value
            return self._run(self._next_after_good(start_value))

    def start(self, start_value, max_iterations=50):
        '''
        Reset the state of the current instance to prepare for a new search and
        start the recursive search by calling the `_run` method.

        __NB__ An optional number of maximum iterations may be specified.  If
        the search takes more than the specified number of iterations before
        finding the boundary-of-interest, an `IndexError` is raised.
        '''
        self._iteration = 0
        self._reset(max_iterations)
        return self._run(start_value)


class LowerBoundFinderBase(BoundFinderBase):
    '''
    Find the lower-bound of values for which the method `evaluate` returns
    `True`.
    '''
    def __init__(self, **kwargs):
        known_bad = kwargs.pop('known_bad', 0)
        known_good = kwargs.pop('known_good', sys.maxint)
        super(LowerBoundFinderBase, self).__init__(known_bad, known_good,
                                                   **kwargs)


class UpperBoundFinderBase(BoundFinderBase):
    '''
    Find the upper-bound of values for which the method `evaluate` returns
    `True`.
    '''
    def __init__(self, **kwargs):
        known_bad = kwargs.pop('known_bad', sys.maxint)
        known_good = kwargs.pop('known_good', 0)
        super(UpperBoundFinderBase, self).__init__(known_bad, known_good,
                                                   **kwargs)


class LowerBoundBisectFinder(LowerBoundFinderBase):
    def _next_after_good(self, value):
        '''
        Since the current run was successful, try to find a lower successful
        value between the current value and the most-recently-failed value.
        '''
        return (self.good - self.bad) / 2 + self.bad

    def _next_after_bad(self, value):
        '''
        Keep doubling the last attempted value until we find a successful
        evaluation.
        '''
        if not self._good_found:
            # We haven't processed a successful evaluation yet, so double
            # the start-value and try again.
            return value * 2
        else:
            # There has been at least one value that has resulted in a
            # successful evaluation.  Since the current value failed
            # evaluation, try a value half-way between the current value
            # and the lowest successful value encountered so far.
            return self._next_after_good(value)


class UpperBoundBisectFinder(UpperBoundFinderBase):
    def _next_after_good(self, value):
        '''
        Since the current run was successful, try to find a higher successful
        value between the current value and the most-recently-failed value.
        '''
        next_value = max((self.bad - self.good) / 2, 1) + self.good
        return next_value

    def _next_after_bad(self, value):
        if not self._good_found:
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


class LowerBoundStepFinder(LowerBoundFinderBase):
    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', 1)
        super(LowerBoundStepFinder, self).__init__(*args, **kwargs)

    def _next_after_good(self, value):
        '''
        Since the current run was successful, try to find a lower successful
        value between the current value and the most-recently-failed value.
        '''
        return (self.good - self.bad) / 2 + self.bad

    def _next_after_bad(self, value):
        '''
        Keep incrementing the last attempted value by `self.step` until we find
        a successful evaluation.
        '''
        if not self._good_found:
            # We haven't processed a successful evaluation yet, so increment
            # the start-value by `self.step` and try again.
            next_value = value + self.step
        else:
            next_value = self._next_after_good(value)
        return next_value


class UpperBoundStepFinder(UpperBoundFinderBase):
    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', 1)
        super(UpperBoundStepFinder, self).__init__(*args, **kwargs)

    def _next_after_good(self, value):
        '''
        Since the current run was successful, try to find a higher successful
        value between the current value and the most-recently-failed value.
        '''
        next_value = max((self.bad - self.good) / 2, 1) + self.good
        return next_value


    def _next_after_bad(self, value):
        '''
        Keep decrementing the last attempted value by `self.step` until we find
        a successful evaluation.
        '''
        if not self._good_found:
            # We haven't processed a successful evaluation yet, so decrement
            # the start-value by `self.step` and try again.
            next_value = value - self.step
        else:
            # There has been at least one value that has resulted in a
            # successful evaluation.  Since the current value failed
            # evaluation, try a value half-way between the current value
            # and the lowest successful value encountered so far.
            next_value = self._next_after_good(value)
        return next_value


class BisectLowerBound(LowerBoundBisectFinder):
    def evaluate(self, value):
        result = (value >= self.known_good)
        print '[evaluate] value=%s (%s)' % (value, result)
        return result


class BisectUpperBound(UpperBoundBisectFinder):
    def evaluate(self, value):
        result = (value <= self.known_good)
        print '[evaluate] value=%s (%s)' % (value, result)
        return result


class StepLowerBound(LowerBoundStepFinder):
    def evaluate(self, value):
        result = (value > self.known_bad and value >= self.known_good)
        print '[evaluate] value=%s (%s)' % (value, result)
        return result


class StepUpperBound(UpperBoundStepFinder):
    def evaluate(self, value):
        result = (value >= self.known_good and value < self.known_bad)
        print '[evaluate] value=%s (%s)' % (value, result)
        return result
