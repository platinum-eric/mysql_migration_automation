# mysql_migration_automation

> A script for automating the migration of MySQL database data using concurrent threads.
> Based on driving execute BASH commands (mysqldump and mysql) via python to achive the purpose of migration.
> It's just a primary version to meet the most basic requirement to migration and not perfect tool for now. 

## Introduct
- __Main running script__:
  - _do_migration.py_:  The enterance and only one launching script for this automation sciprt

- __Config file__:
  - _config.yaml_:  Load all your configurations you required
  - _data_obj.yaml_:  The data objects in your database, including both schemas and tables, are ready for migration. Additionally, you have the option to migrate only schemas or only tables.
