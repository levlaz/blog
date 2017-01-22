from setuptools import setup

setup(
    name='blog',
    description='Simple single user blog written in Python 3 and Flask',
    version='1.0.1',
    author='Lev Lazinskiy',
    author_email='lev@levlaz.org',
    license='AGPLv3.0',
    packages=['blog'],
    include_package_data=True,
    install_requires=[
        'flask',
        'python-slugify',
        'markdown',
    ],
)
