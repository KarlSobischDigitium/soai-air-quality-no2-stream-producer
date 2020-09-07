from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='SOAI', version='1.0', packages=['SOAI'], install_requires=requirements)
