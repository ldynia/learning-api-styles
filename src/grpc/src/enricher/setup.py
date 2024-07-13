import os
from setuptools import setup, find_packages


def get_package_name():
    return os.path.basename(os.path.dirname(__file__))


def get_package_version():
    version_file = os.path.join(
        os.path.dirname(__file__), get_package_name(), "__version__.py"
    )
    with open(version_file, "r") as f:
        version_line = f.read().strip()
        version = version_line.split("=")[-1].strip().strip("'\"")
        return version


setup(
    name=get_package_name(),
    version=get_package_version(),
    packages=find_packages(),
    install_requires=[
        "grpcio",
        "grpcio-status",
        "googleapis-common-protos",
        "protobuf",
    ],
    include_package_data=True,
    package_data={
        "enricher.proto": ["*.proto"],
    },
)
