#define _GNU_SOURCE
#define _POSIX_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include <signal.h>
#include <pthread.h>
#include <errno.h>
#include <unistd.h>

#include <sys/wait.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/types.h>

#include "runner.h"
#include "killer.h"
#include "logger.h"

void init_result(struct result *_result) {
    _result->result = _result->error = SUCCESS;
    _result->cpu_time = _result->real_time = _result->signal = _result->exit_code = 0;
    _result->memory = 0;
}


void run(struct config *_config, struct result *_result) {
    // init log fp
    FILE *log_fp = log_open(_config->log_path);

    // init result
    init_result(_result);

    // check whether current user is root
    uid_t uid = getuid();
    if (uid != 0) {
        ERROR_EXIT(ROOT_REQUIRED);
    }

    // check args
    if ((_config->max_cpu_time < 1 && _config->max_cpu_time != UNLIMITED) ||
        (_config->max_real_time < 1 && _config->max_real_time != UNLIMITED) ||
        (_config->max_stack < 1) ||
        (_config->max_memory < 1 && _config->max_memory != UNLIMITED) ||
        (_config->max_process_number < 1 && _config->max_process_number != UNLIMITED) ||
        (_config->max_output_size < 1 && _config->max_output_size != UNLIMITED)) {
        ERROR_EXIT(INVALID_CONFIG);
    }

    // record current time
    struct timeval start, end;
    gettimeofday(&start, NULL);

    pid_t child_pid = fork();

    // pid < 0 shows clone failed
    if (child_pid < 0) {
        ERROR_EXIT(FORK_FAILED);
    }
    else if (child_pid == 0) {
        child_process(log_fp, _config);
    }
    else if (child_pid > 0){
        // create new thread to monitor process running time
        pthread_t tid = 0;
        if (_config->max_real_time != UNLIMITED) {
            struct timeout_killer_args killer_args;

            killer_args.timeout = _config->max_real_time;
            killer_args.pid = child_pid;
            if (pthread_create(&tid, NULL, timeout_killer, (void *) (&killer_args)) != 0) {
                kill_pid(child_pid);
                ERROR_EXIT(PTHREAD_FAILED);
            }
        }

        int status;
        struct rusage resource_usage;

        // wait for child process to terminate
        // on success, returns the process ID of the child whose state has changed;
        // On error, -1 is returned.
        int wait_status = wait4(child_pid, &status, WSTOPPED, &resource_usage);
        if (wait_status == -1) {
            LOG_WARNING(log_fp, "Couldn't wait for process! %s", wait_status);
            kill_pid(child_pid);
            ERROR_EXIT(WAIT_FAILED);
        }
        // get end time
        gettimeofday(&end, NULL);
        _result->real_time = (int) (end.tv_sec * 1000 + end.tv_usec / 1000 - start.tv_sec * 1000 - start.tv_usec / 1000);

        // process exited, we may need to cancel timeout killer thread
        if (_config->max_real_time != UNLIMITED) {
            int cancel_thread_status = pthread_cancel(tid);
            if (cancel_thread_status != 0) {
                // 3 means No Process Found which means the thread already exited before
                if (cancel_thread_status != 3) {
                    LOG_WARNING(log_fp, "Couldn't cancel the thread %d! Error %d %s ", tid, cancel_thread_status, strerror(cancel_thread_status));
                }
            }
        }

        if (WIFSIGNALED(status) != 0) {
            _result->signal = WTERMSIG(status);
        }

        if(_result->signal == SIGUSR1) {
            _result->result = SYSTEM_ERROR;
        }
        else {
            _result->exit_code = WEXITSTATUS(status);
            _result->cpu_time = (int) (resource_usage.ru_utime.tv_sec * 1000 +
                                       resource_usage.ru_utime.tv_usec / 1000);
            _result->memory = resource_usage.ru_maxrss * 1024;

            if (_result->exit_code != 0) {
                _result->result = RUNTIME_ERROR;
                LOG_DEBUG(log_fp, "Failed with signal %d", _result->signal);
            }

            if (_result->signal == SIGSEGV) {
                if (_config->max_memory != UNLIMITED && _result->memory > _config->max_memory) {
                    _result->result = MEMORY_LIMIT_EXCEEDED;
                }
                else {
                    _result->result = RUNTIME_ERROR;
                    LOG_DEBUG(log_fp, "Failed with signal %d %s", _result->signal, strsignal(_result->signal));
                }
            }
            else {
                if (_result->signal != 0) {
                    _result->result = RUNTIME_ERROR;
                    LOG_DEBUG(log_fp, "Failed with signal %d %s", _result->signal, strsignal(_result->signal));
                }
                if (_config->max_memory != UNLIMITED && _result->memory > _config->max_memory) {
                    _result->result = MEMORY_LIMIT_EXCEEDED;
                }
                if (_config->max_real_time != UNLIMITED && _result->real_time > _config->max_real_time) {
                    _result->result = REAL_TIME_LIMIT_EXCEEDED;
                }
                if (_config->max_cpu_time != UNLIMITED && _result->cpu_time > _config->max_cpu_time) {
                    _result->result = CPU_TIME_LIMIT_EXCEEDED;
                }
            }
        }

        log_close(log_fp);
    }
}
