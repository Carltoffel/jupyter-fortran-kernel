from setuptools import setup

setup(name='jupyter_fortran_kernel',
      version='0.1.0',
      description='Minimalistic Fortran kernel for Jupyter',
      author='Carl Burkert',
      author_email='ca.bu@posteo.de',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
      ],
      url='https://github.com/Carltoffel/jupyter-fortran-kernel',
      download_url='https://github.com/Carltoffel/jupyter-fortran-kernel/tarball/0.1.0',
      packages=['jupyter_fortran_kernel'],
      scripts=['jupyter_fortran_kernel/install_fortran_kernel'],
      keywords=['jupyter', 'notebook', 'kernel', 'fortran'],
      include_package_data=True
      )
