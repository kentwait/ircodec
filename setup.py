import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ircodec',
    version='0.1.0.post1',
    author='Kent Kawashima',
    author_email='kentkawashima@gmail.com',
    description='Send and receive IR commands using pigpio',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/kentwait/ircodec',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords = ['pigpio', 'ir', 'raspberry', 'pi'],
    install_requires=[
        'pigpio',
    ],
)