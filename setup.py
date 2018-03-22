from setuptools import setup

setup(name='dataview',
      version='0.1',
      description='Package to quickly view data arrays',
      author='Jens Petersen',
      author_email='jens.petersen@dkfz.de',
      license='MIT',
      packages=['dataview'],
      install_requires=['numpy', 'matplotlib', 'qtpy'],
      zip_safe=True)
