import setuptools

setuptools.setup(
    name="common-log",
    git_version=True,
    author="Stratoscale",
    author_email="stratoscale@stratoscale.com",
    description=("common-log"),
    license="BSD",
    keywords="library",
    url="http://packages.python.org/common-log",
    install_requires=["dateparser==1.1.0"
                      "PyYAML==6.0",
                      "simplejson==3.17.6"]
)
