from setuptools import setup, find_packages

setup(
    name="regimereport",
    version="1.0.0",
    description="Daily market regime report generator and mailer",
    author="Regime Report Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "tushare>=1.2.89",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "regimereport=regimereport.main:run",
        ],
    },
)
