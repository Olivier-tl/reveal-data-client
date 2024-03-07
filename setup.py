import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reveal_data_client",
    version="0.1.0",
    author="BIOS",
    author_email="info@bios.health",
    description="A python package to read the REVEAL dataset.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Olivier-tl/reveal-data-client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_data={
        "reveal_data_client": ["py.typed"],
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=[],
)
