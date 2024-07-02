# mysql_migration_automation

> A script for automated migrating MySQL database data by concurrent thread mode

# Introduct
- __Main running script__:
  - _do_migration.py_:  the enterance and only one launching script for this automation sciprt

- __Config file__:
  - _config.yaml_:  load all your configurations you need
  - _data_obj.yaml_:  The data objects in your database, including both schemas and tables, are ready for migration. Additionally, you have the option to migrate only schemas or only tables.
