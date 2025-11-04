from setuptools import setup, find_packages

setup(
    name="py-browser-automation",
    version="0.2.1",
    author="pUrGe12",
    author_email="achintya.jai@owasp.org",
    url="https://github.com/FauvidoTechnologies/PyBrowserAutomation",
    description="Automate online browsing using python and AI",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "pyba = pyba.cli.main:main",
        ],
    },
    python_requires=">=3.8",
)
