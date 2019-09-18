import setuptools
import sys
import os
__directory__=os.path.dirname(os.path.realpath(__file__))
os.chdir(__directory__)

def read_text(file_name):
    with open(file_name) as file:
        return file.read()

setuptools.setup(
    name='aws-configure',
    version='2.0.0',
    author="Bengt Brodersen",
    author_email="me@qoomon.me",
    description="A CLI to configure AWS named profiles in ~/.aws/config and ~/.aws/credentials files",
    long_description=read_text("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/qoomon/aws-configure",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Systems Administration",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators"
    ],
    install_requires=[
        'awscli',
        'botocore'
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'aws-configure = aws_configure.cli:main',
        ]
    }
)
