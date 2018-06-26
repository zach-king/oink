from setuptools import setup

setup(name='oink',
      version='0.2.0',
      description='A CLI budgeting tools for nerds.',
      url='http://github.com/zach-king/oink',
      author='Zachary King',
      author_email='kingzach77@gmail.com',
      entry_points = {
        'console_scripts': ['oink=oink.cli:main'],
      },
      license='MIT',
      packages=['oink', 'oink.reporting'],
      install_requires=[
        'click',
        'tabulate',
      ],
      zip_safe=False)
