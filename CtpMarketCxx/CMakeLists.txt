cmake_minimum_required(VERSION 2.8)
project(CtpMarketCxx)

set(CMAKE_CXX_STANDARD 11)

set(Boost_USE_MULTITHREADED      ON)
find_package(Boost 1.59.0 COMPONENTS  thread date_time system chrono REQUIRED)
link_directories(/usr/local/lib ctpapi/x64_linux)
link_libraries( boost_system boost_thread boost_date_time thostmduserapi pthread hiredis redis++ jsoncpp )
add_executable(CtpMarketCxx main.cpp market.cpp app.cpp config.cpp logger.cpp service.cpp)