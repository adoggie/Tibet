
Ctp python编译
------
1. 官方提供的ctp 库文件 `libthostmduserapi.so`,`libhosttraderapi.so`,但未提供
`vnctptd.so`,   `vnctpmd.so`的python封装库。这两个需要用户自行编译。 

环境：

    Centos 7.3
    Python 2.7.14 / anaconda 2.7.14
    Boost 1.59 
    Cmake 2.8+
    
    > yum install python-devel

Boost: 

    Download boost 
    ./boostrap.sh —with-python=/usr/local/bin/python
    ./b2
    ./b2 install 

Vnctpmd.so/VnctpTd.so
    
    修改 CMakeLists.txt  
    保证： 
        find_package(Boost 1.59.0 COMPONENTS ..
        PYTHON_INCLUDE_PATH 为 /usr/local/include/python2.7 
        
    > cd vnpy/api/ctp
    > bash ./build.sh
    
TA-lib
    
    下载： 
    ta-lib-0.4.0-src.tar.gz （ source code 官网)
    TA-Lib-0.4.16.tar.gz    (python 接口封装 pypi.python.org)
    
    > tar xvzf ta-lib-0.4.0-src.tar.gz
    > ./configure & make & make install 
    
    > pip install TA-Lib-0.4.16.tar.gz
    
将以上编译和相关的库.so 全部安装或拷贝到 /usr/local/lib 

修改 `~/.bash_profile ` ,添加环境变量

    export LD_LIBRARY_PATH=/usr/local/lib
    eexport PYTHONPATH=<Tibet目录>
    