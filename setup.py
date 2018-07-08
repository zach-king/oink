from setuptools import setup

setup(
    name='oink-cli',
      version='0.3.2',
      description='A CLI budgeting tools for nerds.',
      url='http://github.com/zach-king/oink',
      download_url = 'https://github.com/zcking/oink/archive/0.3.2.tar.gz',
      author='Zachary King',
      author_email='kingzach77@gmail.com',
      entry_points = {
        'console_scripts': ['oink=oink.cli:main'],
      },
      license='MIT',
      packages=['oink', 'oink.reporting'],
      install_requires=[
        'click==6.4',
        'tabulate==0.8.2',
      ],
      setup_requires=[
        'click==6.4',
        'tabulate==0.8.2',
      ],
      zip_safe=False,
      python_requires='>=3.6',
)
