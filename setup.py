import setuptools
import subprocess
import re


def version():
    git_describe_cmd = ["git", "describe", "--tags", "HEAD"]
    git_head_tag = subprocess.check_output(git_describe_cmd).strip().decode("utf-8")
    python_version = git_head_tag
    unofficial_tag = re.search(r"(?=.*)-(\d+)-", python_version)
    if unofficial_tag:
        pep_440_suffix = ".dev{}+".format(unofficial_tag.group(1))
        python_version = python_version.replace(unofficial_tag.group(0), pep_440_suffix)
    return python_version


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="strato_common_log",
    packages=setuptools.find_packages(where="py"),
    package_dir={"": "py"},
    version=version(),
    python_requires="<=2.7.18",
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
)
