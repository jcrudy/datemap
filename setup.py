from setuptools import setup, find_packages
import versioneer
setup(name='datemap',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      author='Jason Rudy',
      author_email='jcrudy@gmail.com',
      url='https://github.com/jcrudy/datemap',
      packages=find_packages(),
      requires=['interval>=1.0.0']
     )