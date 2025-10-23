from setuptools import setup, find_packages

setup(
    name="py-browser-automation",
    version="0.1.4",
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
    python_requires=">=3.8",
)
