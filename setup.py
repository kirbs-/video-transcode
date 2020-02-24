from setuptools import setup
import sys
# from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call

#
# class PostDevelopCommand(develop):
#     """Post-installation for development mode."""
#     def run(self):
#         check_call("apt-get install this-package".split())
#         develop.run(self)


class InstallSystemServiceCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        check_call("apt-get install this-package".split())
        install.run(self)


setup(name='video-transcode',
      version='1.0.0',
      url='https://github.com/kirbs-/video-transcode',
      description='Video commercial cutting and transcoding stack.',
      author='Chris Kirby',
      author_email='kirbycm@gmail.com',
      license='MIT',
      packages=['video-transcode'],
      package_data={'video-transcode': [os.path.join('config', '*')]},
      install_requires=['celery', 'pyyaml>=5.1', 'pendulum'],
      zip_safe=False,
      cmdclass={
            'install': InstallSystemServiceCommand,
      },
)