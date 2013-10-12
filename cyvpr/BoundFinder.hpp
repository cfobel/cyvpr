#ifndef ___BOUND_FINDER__HPP___
#define ___BOUND_FINDER__HPP___

#include <stdexcept>
#include <limits>
#include "Formatter.hpp"


namespace bound_finder {

template <typename T>
class Evaluator {
public:
    virtual bool operator() (T value) = 0;
};


template <typename T>
class BoundFinderBase {
public:
    /*
     * This class provides an API for finding a boundary-value for a monotonic
     * function, _i.e., an upper-bound or lower-bound on a parameter that
     * results in a successful evaluation of the user-defined `evaluate`
     * method.
     *
     * By calling the `start` method with some initial value, several
     * iterations of evaluation are performed to find the boundary value of
     * interest.
     *
     * __NB__ This class is an abstract-base-class, since it does not provide a
     * default implementation for the following methods:
     *
     *   * `evaluate`
     *   * `_next_after_bad`
     *   * `_next_after_good`
     */

    T known_bad_;
    T known_good_;
    Evaluator<T> *evaluator_;
    T bad_;
    T good_;
    int max_iterations_;
    int iteration_;
    bool good_found_;

    BoundFinderBase() : evaluator_(NULL) {}

    /*
     * Return `true` to indicate success for the provided value, or `false` to
     * indicate failure.  This result is used to guide the search to the
     * boundary of interest.
     */
    virtual bool evaluate(T value) const {
        if (evaluator_ == NULL) {
            throw std::runtime_error("No evaluator has been set.");
        } else {
            return (*this->evaluator_)(value);
        }
    }

    /*
     * Given a value that failed evaluation, propose a new value to evaluate.
     */
    virtual T next_after_bad(T value) const = 0;

    /*
     * Given a value that resulted in a successful evaluation, propose a new
     * value to evaluate to try to tighten the bound.
     */
    virtual T next_after_good(T value) const = 0;


    virtual void init(Evaluator<T> *evaluator, T known_bad, T known_good) {
        this->evaluator_ = evaluator;
        this->known_bad_ = known_bad;
        this->known_good_ = known_good;
    }

    T starting_bad() const { return this->known_bad_; }
    T starting_good() const { return this->known_good_; }

    void reset(int max_iterations) {
        /*
         * Reset the state of the finder to prepare for a new search.
         */
        this->bad_ = this->starting_bad();
        this->good_ = this->starting_good();
        this->max_iterations_ = max_iterations;
        this->iteration_ = 0;
        this->good_found_ = false;
    }

    T run(T start_value) {
        /*
         * Perform a recursive search to find the boundary of interest, by
         * successively evaluating potential values.  After each evaluation, the
         * `_next_after_bad` and `_next_after_good` methods are used to determine
         * the next value to try.

         * __NB__ TODO: Look up terminology for recursive strategies in
         * "Structured Parallel Programming".  They provide a term for what I call
         * `exit` here.

         * The recursive calls exit when the proposed test value is the same as
         * the most-recently tested value that failed the evaluation.  In this
         * case, we know that we have encountered the transition from `good` to
         * `bad`, _i.e., we have found the boundary_.
         */
        this->iteration_++;
        if (this->iteration_ >= this->max_iterations_) {
            throw std::runtime_error(Formatter() << "Maximum number of iterations ("
                                     << this->max_iterations_ << ") reached.");
        }
        if (this->good_found_ && this->bad_ == start_value) {
            /*
             * We have arrived back at the most-recently-failed value, so it's
             * time to stop, returning the lowest-successful value we found
             * along the way.
             */
            return this->good_;
        }
        bool result = this->evaluate(start_value);
        if (!result) {
            this->bad_ = start_value;
            return this->run(this->next_after_bad(start_value));
        } else {
            this->good_found_ = true;
            this->good_ = start_value;
            return this->run(this->next_after_good(start_value));
        }
    }

    T start(T start_value, int max_iterations=50) {
        /*
         * Reset the state of the current instance to prepare for a new search
         * and start the recursive search by calling the `_run` method.
         *
         * __NB__ An optional number of maximum iterations may be specified.
         * If the search takes more than the specified number of iterations
         * before finding the boundary-of-interest, a `std::runtime_error` is
         * thrown.
         */
        this->iteration_ = 0;
        this->reset(max_iterations);
        return this->run(start_value);
    }
};


template <typename T>
class LowerBoundFinderBase : public BoundFinderBase<T> {
public:
    LowerBoundFinderBase() : BoundFinderBase<T>() {}

    /*
     * Find the lower-bound of values for which the method `evaluate` returns
     * `true`.
     */
    virtual void init(Evaluator<T> *evaluator, T max_evaluate_value,
                      T known_bad=0) {
        BoundFinderBase<T>::init(evaluator, known_bad, max_evaluate_value);
    }
};


template <typename T>
class UpperBoundFinderBase : public BoundFinderBase<T> {
public:
    UpperBoundFinderBase() : BoundFinderBase<T>() {}

    /*
     * Find the lower-bound of values for which the method `evaluate` returns
     * `true`.
     */
    virtual void init(Evaluator<T> *evaluator, T min_evaluate_value,
                      T known_bad=std::numeric_limits<T>::max()) {
        BoundFinderBase<T>::init(evaluator, known_bad, min_evaluate_value);
    }
};


template <typename T>
class LowerBoundBisectFinder : public LowerBoundFinderBase<T> {
public:
    LowerBoundBisectFinder() : LowerBoundFinderBase<T>() {}

    T next_after_good(T value) const {
        /*
         * Since the current run was successful, try to find a lower successful
         * value between the current value and the most-recently-failed value.
         */
        return (this->good_ - this->bad_) / 2 + this->bad_;
    }

    T next_after_bad(T value) const {
        /*
         * Keep doubling the last attempted value until we find a successful
         * evaluation.
         */
        if (!this->good_found_) {
            /*
             * We haven't processed a successful evaluation yet, so double
             * the start-value and try again.
             */
            return value * 2;
        } else {
            /*
             * There has been at least one value that has resulted in a
             * successful evaluation.  Since the current value failed
             * evaluation, try a value half-way between the current value and
             * the lowest successful value encountered so far.
             */
            return this->next_after_good(value);
        }
    }
};


template <typename T>
class LowerBoundStepFinder : public LowerBoundFinderBase<T> {
public:
    T step_;

    virtual void init(Evaluator<T> *evaluator, T max_evaluate_value,
                      T step=1, T known_bad=0) {
        this->step_ = step;
        BoundFinderBase<T>::init(evaluator, known_bad, max_evaluate_value);
    }

    T next_after_good(T value) const {
        /*
         * Since the current run was successful, try to find a lower successful
         * value between the current value and the most-recently-failed value.
         */
        return (this->good_ - this->bad_) / 2 + this->bad_;
    }

    T next_after_bad(T value) const {
        /*
         * Keep incrementing the last attempted value by `this->step_` until we
         * find a successful evaluation.
         */
        T next_value;
        if (!this->good_found_) {
            /*
             * We haven't processed a successful evaluation yet, so increment
             * the start-value by `this->step_` and try again.
             */
            next_value = value + this->step_;
        } else {
            next_value = this->next_after_good(value);
        }
        return next_value;
    }
};

}

#endif
