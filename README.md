README


Helper to consume a database from the REPL.

Dependencies:

* 1) pypyodbc
* 2) tabulate
* 3) Configuration file dbhelper.ini. A template is included in the source.

Sample:

```
#!python

>>> import dbhelper
>>> import dataformatters as df
>>> master = dbhelper.DataBase('master')  # Connection string name from the ini file
>>> master.dbo.sp <TAB>
db.dbo.spt_fallback_db  db.dbo.spt_fallback_usg db.dbo.spt_values
db.dbo.spt_fallback_dev db.dbo.spt_monitor
>>>result = dbo.spt_monitor.select()
>>>df.to_html(result)
Creating and opening temp file C:\Users\smonia\AppData\Local\Temp\tmpn3g43ppp.htm
>>>df.to_csv(result)
Creating and opening temp file C:\Users\smonia\AppData\Local\Temp\tmpe68shxd9.csv
>>>result[0]
row(lastrun=datetime.datetime(2015, 5, 13, 23, 34, 58, 77000), cpu_busy=59, io_busy=29, 
idle=288, pack_received=0, pack_sent=0, connections=12, pack_errors=0, total_read=0, total_write=0, total_errors=0)

```
The data formatter works with iterables using lists, tuples, dictionaries and namedtuples as rows. There's a third option that uses tabulate for output to_console().
Both HTML and CSV options create a temp file and use os.startfile (in Windows you get the default browser and -usually- Excel).

Known issues (help/guidance appreciated!): 

* Must be converted to a real package (to auto install dependencies, etc.)
* Improve query interface (in progress)
* Decide on other SQL features to support beyond querying (UPDATES, INSERTS, etc, would it make sense?)


