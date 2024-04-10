import codecs
import os.path
from setuptools import setup, find_namespace_packages

def read(rel_path):
    # Get the absolute path of the file relative to the current directory
    here = os.path.abspath(os.path.dirname(__file__))
    # Read the contents of the file using the codecs module to handle Unicode
    with codecs.open(os.path.join(here, rel_path), 'r', encoding='utf-8') as fp:
        return fp.read()

def get_version(rel_path):
    """
    Get the package version dynamically.
    This function reads the contents of the specified file and extracts the package version.
    """
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

requirements = [
    'Twisted==21.7.0',
    'pyasn1==0.4.8',
    'cryptography==3.4.8',
    'simplejson==3.17.3',
    'requests==2.26.0',
    'zope.interface==5.4.0',
    'PyPDF2==1.26.0',
    'fpdf==1.7.2',
    'passlib==1.7.4',
    'Jinja2==3.0.1',
    'ntlmlib==0.92',
    'bcrypt==3.2.0',
]

setup(
    name='opencanary',
    version=get_version("opencanary/__init__.py"),
    url='http://www.thinkst.com/',
    author='Thinkst Applied Research',
    author_email='info@thinkst.com',
    description='OpenCanary daemon',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    license='BSD',
    packages=find_namespace_packages(
        exclude=[
            'docs','docs*'
            'opencanary.test','opencanary.test*'
        ]
    ),
    include_package_data=True,
    scripts=['bin/opencanaryd','bin/opencanary.tac'],
    platforms='any',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Framework :: Twisted",
        "Topic :: System :: Networking",
        "Topic :: Security",
        "Topic :: System :: Networking :: Monitoring",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
    ],
)
