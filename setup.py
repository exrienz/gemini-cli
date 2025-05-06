from setuptools import setup, find_packages

setup(
    name='gemini-cli',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'tenacity'
    ],
    entry_points={
        'console_scripts': [
            'gemini=gemini_cli.main:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='CLI wrapper for Gemini 2.0 Flash API',
    keywords='gemini gpt cli ai',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
)
