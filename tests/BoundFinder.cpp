#include <iostream>
#include "BoundFinder.hpp"


using std::cout;
using std::endl;
using namespace bound_finder;


class TestEvaluator : public Evaluator<int> {
    bool operator() (int value) {
        bool result = value >= 37;
        cout << "[TestEvaluator] value=" << value << ", result=" << result << endl;
        return result;
    }
};


int main(int argc, char const* argv[]) {
    TestEvaluator e;
    LowerBoundBisectFinder<int> b;
    LowerBoundStepFinder<int> s;
    b.init(&e, 500);
    s.init(&e, 500, 5);
    cout << "lower-bound = " << b.start(30) << endl;
    cout << "lower-bound = " << s.start(30) << endl;
    return 0;
}
