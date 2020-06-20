cc_library(
    name = "seccomp_rules",
    srcs = [
        "c_cpp.c",
        "c_cpp_file_io.c",
        "general.c",
        "python.c",                   
    ],
    hdrs = ["seccomp_rules.h"],
    deps = ["//:definitions"],
    linkopts = ["-lseccomp"],
    visibility = ["//visibility:public"],
)
