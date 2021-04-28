from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'quant is hard, make it easier.'
LONG_DESCRIPTION = 'xquant is a python 3 package that helps build and test strategies in the field of quantitative finance.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="xquant", 
        version=VERSION,
        author="Dazheng Percival Xu",
        author_email="<percival1205@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pandas', 'numpy', 'plotly'],
        
        keywords=['python', 'quantitative-finance'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Researchers",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)