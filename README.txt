Helper to consume a database from the REPL.

Dependencies:

* pypyodbc
* tabulate
* Configuration file database.ini. A template is included in the source.

Full documentation available in https://github.com/sebasmonia/pyquebec/wiki

Sample:

>>> from pyquebec import pyquebec
>>> from pyquebec import formatters as pf
>>> pyquebec.add('SampleDB', 'connection string here', 'MSSQL') # first use
>>> db = pyquebec.open('SampleDB') # after using add, the db config and schema is cached
>>> db.dbo.<TAB KEY>
db.dbo.Table1  db.dbo.Table2
db.dbo.Table3  db.dbo.Table4
>>>result = db.dbo.Table1.From().go()
>>> pf.to_html(result)
Creating and opening temp file C:\Users\smonia\AppData\Local\Temp\tmpn3g43ppp.htm
>>> pf.to_csv(result)
Creating and opening temp file C:\Users\smonia\AppData\Local\Temp\tmpe68shxd9.csv
>>> result[0]
row(column1=datetime.datetime(2015, 5, 13, 23, 34, 58, 77000), column2=59, column3=29, column4='Sample')

Pypyodbc returns tuples. This library converts them to namedtuples for increased readability and to make it easier to keep playing with the data using filter, map, sorted, etc.

There's a third option in the formatters that uses tabulate for output to_console().
Both HTML and CSV options create a temp file and use os.startfile (in Windows you get the default browser and, usually, Excel).

Roadmap (help/guidance appreciated!): 

* Tested with MSSQL and SQLite. With some configuration should support other engines, and ideally the config should be included in the package.
* The API for querying might need a few tweaks. Suggestions are welcome.
* Decide on other SQL features to support beyond basic querying. UPDATES, INSERTS, GROUP BY, etc, would it make sense? Would this make supporting other products more difficult?
* Needs more unittest!

Contributors:
Sebastián Monía - http://github.com/sebasmonia
Fernando Antivero - http://github.com/ferantivero
