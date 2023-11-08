from setuptools_plugins.version import get_version
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="strato_common_log",
    packages=setuptools.find_packages(where="py"),
    package_dir={"": "py"},
    version=get_version(),
    entry_points={
        'console_scripts': [
            'strato-log = strato.common.log.log2text:main',
        ],
    },
    author="Stratoscale",
    author_email="zcompute@zadarastorage.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Stratoscale/pycommonlog",
    project_urls={
        "Bug Tracker": "https://github.com/Stratoscale/pycommonlog/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
    options={'bdist_wheel': {'universal': True}}
)
