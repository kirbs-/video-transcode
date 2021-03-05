from setuptools import setup
import os


setup(name='video_transcode',
      version='1.6.0',
      url='https://github.com/kirbs-/video-transcode',
      description='Video commercial cutting and transcoding stack.',
      author='Chris Kirby',
      author_email='kirbycm@gmail.com',
      license='MIT',
      packages=['video_transcode'],
      package_data={'video_transcode': [os.path.join('config', '*')]},
      install_requires=['celery==4.4.7', 'pyyaml>=5.1', 'pendulum', 'moviepy', 'redis'],
      zip_safe=False,
      entry_points={
        'console_scripts': ['video-transcode=video_transcode.video_transcode:main']
      }
)