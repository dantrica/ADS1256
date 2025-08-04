from setuptools import setup, find_packages

setup(
    name='ads1256',
    version='1.0.0',
    description='Library to interface with the ADS1256 ADC module using SPI on Raspberry Pi.',
    author='Dantrica (Modified by OpenAI)',
    author_email='your.email@example.com',  # Replace with your email if desired
    url='https://github.com/dantrica/ADS1256',
    packages=find_packages(),
    install_requires=[
        'spidev',
        'RPi.GPIO'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Hardware :: Hardware Drivers'
    ],
    python_requires='>=3.6',
)
