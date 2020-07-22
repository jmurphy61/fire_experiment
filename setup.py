"""Module installation"""
import setuptools

setuptools.setup(
    name="fire_experiment",
    version="0.1.1",
    author="Jones Maxime Murphy III",
    author_email="jones.murphy@onsight.ga",
    description="Simulate a life of early retirement and financial freedom.",
    long_description_content_type="text/markdown",
    keywords="""finance financial freedome independence retirement
        retire early simulation experiment""",
    url="",
    packages=setuptools.find_packages(),
    license=None,
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.8',
    install_requires=[
        "numpy",
        "pandas",
        "openpyxl",
        "matplotlib"
    ],
    entry_points={
        'console_scripts': [
            'fire-experiment=fire_experiment.__main__:main',
        ]
    },
)
