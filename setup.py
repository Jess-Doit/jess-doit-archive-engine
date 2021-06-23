from setuptools import setup, find_namespace_packages

setup(
    name="jdae",
    version="0.1.0",
    author="Jess Doit",
    author_email="doit.jesss@gmail.com",
    description="Jess Doit's Archive Engine",
    url="https://github.com/Jess-Doit/jess-doit-archive-engine",
    packages=find_namespace_packages(),
    install_requires=[
        "youtube_dl",
        "playsound"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True
)
