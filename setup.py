from setuptools import setup

setup(name='arubaCloudManager',
      version='0.1',
      description='allow to easily manage aruba cloud servers from your terminal',
      url='https://github.com/Giuliano1993/arubaCloudManager',
      author='Giuliano Gostinfini',
      author_email='giuliano.gostinfini.93@gmail.com',
      entry_points = {
        "console_scripts": ['acm = acm:main']
        },
      license='MIT',
      packages=['arubaCloudManager'],
      install_requires=[
          'python-dotenv',
          'pyarubacloud',
          'paramiko',
          'pysftp',
      ],
      zip_safe=False)