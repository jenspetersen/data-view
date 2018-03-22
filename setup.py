from setuptools import setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(name='dataview',
      version='0.1',
      description='Package to quickly view data arrays',
      long_description=readme,
      url="https://github.com/jenspetersen/data-view",
      author='Jens Petersen',
      author_email='jens.petersen@dkfz.de',
      license=license,
      packages=['dataview'],
      install_requires=['numpy', 'matplotlib', 'qtpy'],
      entry_points={"gui_scripts": ["dataviewer=dataview.view:main"]},
      data_files=[("share/applications", ["data/dataviewer.desktop"])])
