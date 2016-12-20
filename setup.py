import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-log-analyser',
    version='0.2.4',
    packages=find_packages(),
    install_requires=[
        'boto3==1.3.1',
        'django>=1.7',
    ],
    include_package_data=True,
    license='MIT License',  # example license
    description='A simple Django app to analyse RDS logs using pgbadger.',
    long_description=README,
    url='https://github.com/squadrun/log_analyser',
    author='Ketan Bhatt',
    author_email='ketanbhatt1006@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
