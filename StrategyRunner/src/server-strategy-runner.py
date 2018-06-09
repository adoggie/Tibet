#coding:utf-8

import platform

if platform.system() != 'Windows':
    from gevent.monkey import patch_all
    patch_all()

from mantis.fundamental.application.app import Application,instance,setup

setup(Application).init().run()


