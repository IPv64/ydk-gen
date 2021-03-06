cmake_minimum_required(VERSION 3.0.0)
cmake_policy(SET CMP0048 NEW)
project(ydk_gnmi_test)
set(YDK_UNITTEST_TARGET_NAME "ydk_gnmi_test")

enable_testing()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/CMakeModules/")
set(gnmi_tests_src
        test_core_gnmi.cpp
        test_gnmi_crud.cpp
        test_gnmi_provider.cpp
        test_gnmi_service.cpp
        test_utils.cpp
        main.cpp)

find_library(xml2_location xml2)
find_library(curl_location curl)
find_library(ssh_location ssh)
find_library(ssh_threads_location ssh_threads)
find_library(pcre_location pcre)
find_library(xslt_location xslt)
find_library(pthread_location pthread)
find_library(dl_location dl)
find_library(ydk_location ydk)
find_library(ydk_gnmi_location ydk_gnmi)
find_library(ydk_ydktest_location ydk_ydktest)
find_package(Protobuf REQUIRED)
find_package(GRPC REQUIRED)

set(CMAKE_CXX_FLAGS         "${CMAKE_CXX_FLAGS} -Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "-O2 -DNDEBUG")
if(COVERAGE STREQUAL True)
    set(CMAKE_CXX_FLAGS_DEBUG   "-g3 -O0 -fprofile-arcs -ftest-coverage")
    set(CMAKE_BUILD_TYPE debug)
else()
    set(CMAKE_CXX_FLAGS_DEBUG   "-g3 -O0")
endif()


# set default build type if not specified by user
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE debug)
endif()

#include_directories(
#    ${PROJECT_SOURCE_DIR}/../core/src
#)

add_executable(${YDK_UNITTEST_TARGET_NAME} ${gnmi_tests_src})
set_property(TARGET ${YDK_UNITTEST_TARGET_NAME} PROPERTY CXX_STANDARD 11)
set_property(TARGET ${YDK_UNITTEST_TARGET_NAME} PROPERTY CXX_STANDARD_REQUIRED ON)
target_link_libraries(${YDK_UNITTEST_TARGET_NAME}
    ${ydk_gnmi_location}
    ${ydk_location}
    ${ydk_ydktest_location}
    ${xml2_location}
    ${curl_location}
    ${ssh_location}
    ${ssh_threads_location}
    ${pcre_location}
    ${xslt_location}
    ${pthread_location}
    ${dl_location}
    -rdynamic
    ${GRPC_GRPC++_LIBRARY}
    ${PROTOBUF_LIBRARY}
)

add_test(NAME ${PROJECT_NAME} COMMAND $<TARGET_FILE:${YDK_UNITTEST_TARGET_NAME}>)

configure_file("${PROJECT_SOURCE_DIR}/main.cpp.in" "${PROJECT_SOURCE_DIR}/main.cpp" ESCAPE_QUOTES @ONLY)
