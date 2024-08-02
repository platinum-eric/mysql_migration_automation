# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

setup(
    name='mysql_migration_automation_script',
    version='0.1.0',
    author='Eric Tan',
    description='This is a data migration script between MySQL databases, intended to facilitate my daily work. '
                'It is not a universal script, but feel free to use it if it can help you as well.',
    packages=find_packages(),
    python_requires='>=3.6',
    # install_requires: 自动安装依赖
    install_requires=[
        'yaml',
        'paramiko'
    ]
)
