from setuptools import setup

setup(name='oink',
      version='0.1.0',
      description='A CLI budgeting tools for nerds.',
      url='http://github.com/zach-king/oink',
      author='Zachary King',
      author_email='kingzach77@gmail.com',
      entry_points = {
        'console_scripts': ['oink=oink.cli:main'],
      },
      license='MIT',
      packages=['oink'],
      zip_safe=False)