cmake_minimum_required(VERSION 2.8)
project(CtpTradeCxx)

set(CMAKE_CXX_STANDARD 11)

set(Boost_USE_MULTITHREADED      ON)
#find_package(Boost 1.59.0 COMPONENTS python thread date_time system chrono REQUIRED)
link_directories( /usr/local/lib ctpapi/x64_linux)
#link_directories("/usr/local/lib"  ctpapi/x64_linux )
include_directories(   /usr/local/include /usr/local/Cellar/boost/1.60.0_2/include ctpapi/x64_linux)

#ctpapi/x64_linux
link_libraries(  boost_system boost_thread boost_date_time  thosttraderapi pthread jsoncpp )
add_executable(CtpTradeCxx tradeImpl.cpp tradeImpl.h trade.cpp trade.h main.cpp
        app.cpp config.cpp logger.cpp service.cpp
        http.h http.cpp mongoose.h mongoose.c
        error.h error.cpp http-api.h
        )