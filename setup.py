from setuptools import setup

with open('README.txt') as file:
    long_description = file.read()

setup(
    name = 'pyquebec',
    packages = ['pyquebec'],
    version = '0.9.4',
    description = 'A Python package to create simple SQL queries from the console, and quickly display the returned information.',
    long_description = long_description,
    author='Sebastián Monía',
    author_email='smonia@outlook.com',
    license='MIT',
    url='https://github.com/sebasmonia/pyquebec',
    install_requires=[
        'pypyodbc'],
    keywords='SQL development console MSSQL SQLite',
    package_data = {
                    '' : ['*.txt', '*.md'],
                    'pyquebec' : ['*.ini', 'resources/*.*']
                   },
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development',
        'Topic :: Utilities'
    ]
)