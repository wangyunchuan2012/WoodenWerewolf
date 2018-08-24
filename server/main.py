# coding=utf-8
"""
synopsis: program entry
author: haoranzeus@gmail.com (zhanghaoran)
"""
import codecs
import getopt
import logging.config
import os
import sys
import yaml


def usage():
    print('some usage information')


def main(argv):
    try:
        opts, args = getopt.getopt(
                argv, "c:", ["configure=", "help"])
    except getopt.GetoptError:
        usage()
        sys.exit()

    conf_path = os.path.join(os.path.abspath("."), 'configs/conf')
    for opt, arg in opts:
        if opt == '--help':
            usage()
            sys.exit()
        elif opt in ('-c', '--configure'):
            conf_path = arg
        else:
            usage()
            exit()

    def _exit_w_info(info):
        print('\n%s\n' % info)
        usage()
        exit()

    def _ok_conf(conf):
        def check_cfg(cfg):
            cpath = os.path.join(conf, cfg)
            return ((os.path.exists(cpath) and cpath)
                    or _exit_w_info('missing %s.' % cpath))
        return [check_cfg(cfg) for cfg in ('api.yaml', 'logging.yaml')]

    api_conf, logging_conf = _ok_conf(conf_path)
    app_conf = {}
    log_conf = {}
    with codecs.open(logging_conf, 'r', 'utf-8') as logging_file:
        log_conf_dict = yaml.load(logging_file)
        log_conf.update(log_conf_dict)
        logfile_path = os.path.split(
                log_conf_dict['handlers']['file']['filename'])[0]
        if not os.path.exists(logfile_path):
            os.makedirs(logfile_path)
        logging.config.dictConfig(log_conf_dict)
    with codecs.open(api_conf, 'r', 'utf-8') as conff:
        app_conf.update(yaml.load(conff))
    framework = app_conf['woodenwerewolf']['framework']
    _log = logging.getLogger(__name__)

    # 获取环境变量
    env_dist = os.environ
    appid = env_dist.get('APPID')
    secret = env_dist.get('SECRET')

    # 等logging配置好了再导入
    from utils.context import Context
    context = Context()
    context.init(app_conf)
    # 设置微信的环境变量
    context.appid = appid
    context.secret = secret
    from mysqldal.sql_engine import sql_init

    sql_init()
    if framework == 'flask':
        from RESTFul_flask.app import app
        from RESTFul_flask.app import app_init

        app_init(log_conf_dict)
        _log.debug('**start from main.py**')
        return app, framework
    elif framework == 'bottle':
        from RESTFul_bottle.main import app
        return app, framework


if __name__ == '__main__':
    args = sys.argv[1:]
    app, framework = main(args)
    if framework == 'flask':
        app.run(host="0.0.0.0", debug=True)
    elif framework == 'bottle':
        app.run(host="0.0.0.0", port=5000, server='wsgiref')
else:
    args = sys.argv[1:]
    app, framework = main(args)
