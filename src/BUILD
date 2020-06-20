cc_binary(
    name = "judger",
    srcs = [
        "main.c",
    ],
    deps = [":argtable3", ":runner"],
)

cc_library(
    name = "runner",
    srcs = [
        "runner.c",
    ],
    hdrs = ["runner.h"],
    deps = [":logger", ":child",],
)

cc_library(
    name = "child",
    srcs = [
        "child.c",
    ],
    hdrs = ["child.h"],
    deps = ["//rules:seccomp_rules", ":definitions", ":logger", ":killer"],
    linkopts = ["-pthread"],
)

cc_library(
    name = "definitions",
    hdrs = ["definitions.h"],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "argtable3",
    srcs = [
        "argtable3.c",
    ],
    hdrs = ["argtable3.h"],
)

cc_library(
    name = "killer",
    srcs = [
        "killer.c",
    ],
    hdrs = ["killer.h"],
    linkopts = ["-pthread"],
)

cc_library(
    name = "logger",
    srcs = [
        "logger.c",
    ],
    hdrs = ["logger.h"],
    deps = [":definitions"]
)
