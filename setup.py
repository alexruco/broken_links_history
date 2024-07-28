# setup.py

from setuptools import setup, find_packages

setup(
    name="waybackmachine_site_pages ",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas"
    ],
    author="Alex Ruco",
    author_email="alex@ruco.pt",
    description="A package to check for links on Wayback Machine",
    url="https://github.com/yourusername/waybackmachine_site_pages ",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
