from setuptools import setup, find_packages

setup(
    name="projet", 
    version="0.1.0", 
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'plotly',
    ],
    extras_require={
        'dev': [
            'pytest',
        ]
    },
)