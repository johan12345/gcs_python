from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gcs',
    version_format="{tag}.post{commitcount}+{gitsha}",
    setup_requires=['setuptools-git-version'],
    python_requires='>= 3.7',
    description='Python 3 implementation of the Graduated Cylindrical Shell model (Thernisien, 2011).'
                'Based on the existing IDL implementation in SolarSoft.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/johan12345/gcs_python',
    author='Johan von Forstner',
    author_email='forstner@physik.uni-kiel.de',
    entry_points={
        'console_scripts': [
            'gcs_gui=gcs.gui:main',
        ]
    },
    packages=['gcs', 'gcs.utils'],
    install_requires=['astroquery', 'matplotlib', 'numpy', 'scipy>=1.2.0', 'sunpy[net,jpeg2000]>=2.1.0', 'PyQt5'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
