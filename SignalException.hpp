#include <map>
#include <string>
#include <signal.h>
#include "Formatter.hpp"


class SignalException: public std::runtime_error {
public:
    int signum_;

    static std::map<std::string, int> signal_name_to_num() {
        std::map<std::string, int> signame_to_signum;

        signame_to_signum["SIGHUP"] = 1; /* Hangup (POSIX).  */
        signame_to_signum["SIGINT"] = 2; /* Interrupt (ANSI).  */
        signame_to_signum["SIGQUIT"] = 3; /* Quit (POSIX).  */
        signame_to_signum["SIGILL"] = 4; /* Illegal instruction (ANSI).  */
        signame_to_signum["SIGTRAP"] = 5; /* Trace trap (POSIX).  */
        signame_to_signum["SIGABRT"] = 6; /* Abort (ANSI).  */
        signame_to_signum["SIGIOT"] = 6; /* IOT trap (4.2 BSD).  */
        signame_to_signum["SIGBUS"] = 7; /* BUS error (4.2 BSD).  */
        signame_to_signum["SIGFPE"] = 8; /* Floating-point exception (ANSI).  */
        signame_to_signum["SIGKILL"] = 9; /* Kill, unblockable (POSIX).  */
        signame_to_signum["SIGUSR1"] = 10; /* User-defined signal 1 (POSIX).  */
        signame_to_signum["SIGSEGV"] = 11; /* Segmentation violation (ANSI).  */
        signame_to_signum["SIGUSR2"] = 12; /* User-defined signal 2 (POSIX).  */
        signame_to_signum["SIGPIPE"] = 13; /* Broken pipe (POSIX).  */
        signame_to_signum["SIGALRM"] = 14; /* Alarm clock (POSIX).  */
        signame_to_signum["SIGTERM"] = 15; /* Termination (ANSI).  */
        signame_to_signum["SIGSTKFLT"] = 16; /* Stack fault.  */
        signame_to_signum["SIGCLD"] = SIGCHLD; /* Same as SIGCHLD (System V).  */
        signame_to_signum["SIGCHLD"] = 17; /* Child status has changed (POSIX).  */
        signame_to_signum["SIGCONT"] = 18; /* Continue (POSIX).  */
        signame_to_signum["SIGSTOP"] = 19; /* Stop, unblockable (POSIX).  */
        signame_to_signum["SIGTSTP"] = 20; /* Keyboard stop (POSIX).  */
        signame_to_signum["SIGTTIN"] = 21; /* Background read from tty (POSIX).  */
        signame_to_signum["SIGTTOU"] = 22; /* Background write to tty (POSIX).  */

        return signame_to_signum;
    }

    static std::map<int, std::string> signal_num_to_name() {
        std::map<std::string, int> signame_to_signum = signal_name_to_num();
        std::map<int, std::string> signum_to_signame;

        std::map<std::string, int>::const_iterator i = signame_to_signum.begin();
        for (; i != signame_to_signum.end(); i++) {
            signum_to_signame[i->second] = i->first;
        }

        return signum_to_signame;
    }

    SignalException(int signum)
            : runtime_error(Formatter() << "Caught signal: "
                            << signal_num_to_name()[signum]),
              signum_(signum) {}
    SignalException(int signum, std::string msg)
            : runtime_error(msg), signum_(signum) {}

    std::string signame() const {
        return signal_num_to_name()[this->signum_];
    }
};
