from setuptools import setup, find_packages

setup(
    name="pyba",
    version="0.0.1",
    author="pUrGe12",
    description="Automate online browsing using python and AI",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
