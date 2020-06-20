#include <stdio.h>
#include <seccomp.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>
#include "../definitions.h"

int python_seccomp_rules(struct config *_config) {
    static int syscalls_whitelist[] = {SCMP_SYS(read), SCMP_SYS(fstat),
                                SCMP_SYS(mmap), SCMP_SYS(mprotect),
                                SCMP_SYS(munmap), SCMP_SYS(uname),
                                SCMP_SYS(arch_prctl), SCMP_SYS(brk),
                                SCMP_SYS(access), SCMP_SYS(exit_group),
                                SCMP_SYS(close), SCMP_SYS(readlink),
                                SCMP_SYS(sysinfo), SCMP_SYS(write),
                                SCMP_SYS(writev), SCMP_SYS(lseek),
                                SCMP_SYS(clock_gettime), SCMP_SYS(stat),
                                SCMP_SYS(getdents), SCMP_SYS(lstat),
                                SCMP_SYS(getcwd), SCMP_SYS(rt_sigprocmask),
                                SCMP_SYS(rt_sigaction), SCMP_SYS(ioctl), 
                                SCMP_SYS(set_tid_address), SCMP_SYS(set_robust_list),
                                SCMP_SYS(prlimit64), SCMP_SYS(getrandom),
                                SCMP_SYS(futex), SCMP_SYS(getdents64), 
                                SCMP_SYS(sigaltstack), SCMP_SYS(pread64),
                                SCMP_SYS(dup), SCMP_SYS(fcntl), SCMP_SYS(geteuid),
                                SCMP_SYS(getuid), SCMP_SYS(getegid), SCMP_SYS(getgid),
                                // wtf?
                                SCMP_SYS(socket), SCMP_SYS(connect)
                                };

    int syscalls_whitelist_length = sizeof(syscalls_whitelist) / sizeof(int);
    scmp_filter_ctx ctx = NULL;
    // load seccomp rules
    ctx = seccomp_init(SCMP_ACT_KILL);
    if (!ctx) {
        return LOAD_SECCOMP_FAILED;
    }
    for (int i = 0; i < syscalls_whitelist_length; i++) {
        if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, syscalls_whitelist[i], 0) != 0) {
            return LOAD_SECCOMP_FAILED;
        }
    }
    // add extra rule for execve
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(execve), 1, SCMP_A0(SCMP_CMP_EQ, (scmp_datum_t)(_config->exe_path))) != 0) {
        return LOAD_SECCOMP_FAILED;
    }


    // do not allow "w" and "rw"
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 1, SCMP_CMP(1, SCMP_CMP_MASKED_EQ, O_WRONLY | O_RDWR, 0)) != 0) {
        return LOAD_SECCOMP_FAILED;
    }
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(openat), 1, SCMP_CMP(2, SCMP_CMP_MASKED_EQ, O_WRONLY | O_RDWR, 0)) != 0) {
        return LOAD_SECCOMP_FAILED;
    }

    if (seccomp_load(ctx) != 0) {
        return LOAD_SECCOMP_FAILED;
    }
    seccomp_release(ctx);
    return 0;
}
