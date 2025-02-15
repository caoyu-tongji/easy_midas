from setuptools import setup, find_packages

setup(
    name="structural_analysis",
    version="0.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="A structural analysis post-processing package for MIDAS Civil",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/structural-analysis",
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
        'pandas>=1.2.0',
        'numpy>=1.19.0',
        'matplotlib>=3.3.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Civil Engineering"
    ],
    python_requires='>=3.7'
) 