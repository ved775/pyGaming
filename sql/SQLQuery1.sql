create database pygaming;

create login pygaming with Password = 'pygaming';

alter server role sysadmin add member pygaming;

select name from sys.sql_logins where name = 'pygaming';