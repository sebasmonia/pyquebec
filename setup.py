from distutils.core import setup

setup(
    name = 'zoidberg',
    packages = ['zoidberg'],
    version = '0.5.0',
    description = 'A Python package to create quick SQL queries from the console, and quickly display the returned information.',
    author='Sebastián Monía',
    author_email='smonia@outlook.com',
    url='https://github.com/sebasmonia/zoidberg',
    install_requires='pypyodbc,tabulate'
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Software Development',
        'Topic :: Utilities'
    ]
)