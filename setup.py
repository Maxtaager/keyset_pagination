from setuptools import setup, find_packages
from keyset_pagination import __version__, __author__, __email__

setup(
    name='django-keyset-pagination',
    version=__version__,
    description='Keyset pagination for django',
    author=__author__,
    author_email=__email__,
    zip_safe=False,
    include_package_data=False,
    packages=find_packages('.', include=('keyset_pagination', )),
    install_requires=[
        open("requirements.txt").readlines(),
    ],
)