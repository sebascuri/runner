from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name="lsf-runner",
    version="0.0.5",
    author="Sebastian Curi",
    author_email="sebascuri@gmail.com",
    description="A package to run experiments on lsf or linux clusters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sebascuri/runner",
    license="MIT",
    packages=find_packages(exclude=['docs']),
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    extras_require={
        'test': [
            'pytest>=5.0,<5.1',
            'flake8>=3.7.8,<3.8',
            'pydocstyle==4.0.0',
            'pytest_cov>=2.7,<3',
            'mypy>=0.740',
        ],
    },
)
