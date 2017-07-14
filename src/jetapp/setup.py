__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

from setuptools import setup, find_packages

# parse requirements
req_lines = [line.strip() for line in open(
    'requirements.txt').readlines()]
install_reqs = list(filter(None, req_lines))

setup(
    name="snabb-junos",
    namespace_packages=['jnpr'],
    version="0.0.1",
    author="Amish Anand",
    author_email="jet-hackers@juniper.net",
    description=("Junos Snabb Integration JET app"),
    license="Apache 2.0",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=install_reqs,
    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Other Scripting Engines',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Firewalls',
        'Topic :: Text Processing :: Markup :: XML'
    ],
)
