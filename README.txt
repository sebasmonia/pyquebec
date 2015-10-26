Helper to consume a database from the REPL.

Dependencies:

* pypyodbc
* tabulate
* Configuration file dbhelper.ini. A template is included in the source.

Sample:

>>> from pyquebec import database
>>> from pyquebec import dataformatters as qf
>>> master = database.connect('master')  # Connection string name from the ini file, or a entire conn string
>>> master.dbo.sp <TAB KEY>
db.dbo.spt_fallback_db  db.dbo.spt_fallback_usg db.dbo.spt_values
db.dbo.spt_fallback_dev db.dbo.spt_monitor
>>>result = db.dbo.spt_monitor.From().go()
>>> qf.to_html(result)
Creating and opening temp file C:\Users\smonia\AppData\Local\Temp\tmpn3g43ppp.htm
>>> qf.to_csv(result)
Creating and opening temp file C:\Users\smonia\AppData\Local\Temp\tmpe68shxd9.csv
>>> result[0]
row(lastrun=datetime.datetime(2015, 5, 13, 23, 34, 58, 77000), cpu_busy=59, io_busy=29, 
idle=288, pack_received=0, pack_sent=0, connections=12, pack_errors=0, total_read=0, total_write=0, total_errors=0)

Pypyodbc returns tuples by default. This library converts them to namedtuples for increased readability and to make it easier to keep playing with the data using filter, map, etc.

The formatters work with iterables using lists, tuples, dictionaries and namedtuples as rows. There's a third option that uses tabulate for output to_console().
Both HTML and CSV options create a temp file and use os.startfile (in Windows you get the default browser and -usually- Excel).

Roadmap (help/guidance appreciated!): 

* Other alternatives in PyPI didn't support SQL Server. This one was tested using SQL Server, but should work with other RDBMS with minimal effort. The final aim is to support as many as possible (all?).
* The API for querying might need a few tweaks. Suggestions are welcome.
* Decide on other SQL features to support beyond basic querying. UPDATES, INSERTS, GROUP BY, etc, would it make sense? Would this make supporting other products more difficult?
* Needs unittest!