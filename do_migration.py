# ***************************************************************************************************************************

# This script for migrating MySQL data object to another MySQL database, it's suitable for the version from 5.7 to above.
# The major method is by using [mysqldump] to dump and [mysql] to read to proceed the migration.


# Config:
#       ./config.yaml

# Input Format:
#   read data object name for ./data_objects.yaml by def []
#       1.only schema - e.g.config
#       2.schema_name.table_name - e.g.config.defaults

# Output:
#   None

# ***************************************************************************************************************************

# -*- coding: utf-8 -*-

import yaml
import time
import paramiko
import concurrent.futures


class Logging:
    """ Output log content with standardized format. """

    @staticmethod
    def current_time():
        """ * Static Method * to generate standardized time format"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    @classmethod
    def info(cls, content):
        """ * Class Method * to Regular log outputting function"""
        print(f"[{cls.current_time()}] [Info] [{content}]")

    @classmethod
    def warning(cls, content):
        """ * Class Method * to Warning outputting function"""
        print(f"[{cls.current_time()}] [Warning] [{content}]")

    @classmethod
    def error(cls, content):
        """ * Class Method * to output when crush or issue occurs"""
        print(f"[{cls.current_time()}] [Error] [{content}]")

    @classmethod
    def result(cls, content):
        """ * Class Method * to output when crush or issue occurs"""
        print(f"[{cls.current_time()}] [Result] [{content}]")


class SSHConnector:
    """ Define class and relevant functions to run command conveniently via SSH tunnel by using Paramiko package. """

    def __init__(self, host, username, password, port=22):
        self.ip = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None

    def connect(self):
        """ Build connection to target server
        """
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if self.password != '':
                self.connection.connect(self.ip, self.port, self.username, (str(self.password)), timeout=5.0)
            else:
                try:
                    self.connection.connect(self.ip, self.port, self.username, look_for_keys=False,
                                            allow_agent=False, timeout=5.0)
                except paramiko.ssh_exception.SSHException:
                    self.connection.get_transport().auth_none(self.username)
                self.connection.sftp = paramiko.SFTPClient.from_transport(self.connection.get_transport())
            Logging.info(f"Successfully established connection to {self.ip}")

        except Exception as e:
            try:
                print(str(e.args))
                self.connection = None
            finally:
                e = None
                del e

    def close(self):
        """ Close the connection to improve security.
        """
        if self.connection:
            self.connection.close()
            Logging.info("SSH connection has been closed safely")
            self.connection = None
        else:
            Logging.warning("No connection need to be closed, please check your coding")


def decode_result(content):
    """ Convert a byte string to a readable string, typically used for outputs from running Bash commands.
    """
    if isinstance(content, bytes):
        return bytes.decode(content)
    else:
        content = None
        Logging.error("There is no byte string to convert, please check the coding")


def load_configs(config_path='./config.yaml'):
    """ Load configurations from .yaml file
    """
    return yaml.load(open(config_path), Loader=yaml.FullLoader)


def load_data_obj(input_path='./data_obj.yaml'):
    """ Load data objects from .yaml file
    """
    input_objs = yaml.load(open(input_path), Loader=yaml.FullLoader)
    schemas = input_objs.get('schemas', '')
    tables = input_objs.get('tables', '')

    # data_objs = {}
    # if schemas and tables:
    #     data_objs.setdefault('schemas', schemas.strip().split(' '))
    #     data_objs.setdefault('tables', tables.strip().split(' '))
    # elif schemas and not tables:
    #     data_objs.setdefault('schemas', schemas.strip().split(' '))
    # elif tables and not schemas:
    #     data_objs.setdefault('tables', tables.strip().split(' '))
    # else:
    #     Logging.warning("There are no data objects in the input file, please check your inputs.")
    #
    # return data_objs

    data_objs_list = []
    if schemas and tables:
        data_objs_list = schemas.strip().split(' ') + tables.strip().split(' ')
    elif schemas and not tables:
        data_objs_list = schemas.strip().split(' ')
    elif tables and not schemas:
        data_objs_list = tables.strip().split(' ')
    else:
        Logging.warning("There are no data objects in the input file, please check your inputs.")

    return data_objs_list


def generate_commands_list(configs, data_obj):
    """ Extract input to generate corresponding BASH command to execute
        Input Format:
            1. only schema - e.g. config
            2. schema_name.table_name - e.g. config.defaults
    """

    if '.' in data_obj:
        schema, table = data_obj.split('.')
        return configs.get('template_commands', {}).get('dump_and_read_table', '').format(
            export_password=configs.get('export_database', {}).get('password', ''),
            export_username=configs.get('export_database', {}).get('username', ''),
            schema=schema,
            table=table,
            import_database=configs.get('import_database', {}).get('host', ''),
            import_password=configs.get('import_database', {}).get('password', ''),
            import_username=configs.get('import_database', {}).get('username', ''))
    else:
        schema = data_obj
        return configs.get('template_commands', {}).get('dump_and_read_schema', '').format(
            export_password=configs.get('export_database', {}).get('password', ''),
            export_username=configs.get('export_database', {}).get('username', ''),
            schema=schema,
            import_database=configs.get('import_database', {}).get('host', ''),
            import_password=configs.get('import_database', {}).get('password', ''),
            import_username=configs.get('import_database', {}).get('username', ''))


def main():
    """
        Migrate data by concurrent threads mode
        max_thread_number: from setting , at least 4 threads
    """
    Logging.info("The migration program is starting now")

    configs = load_configs()
    data_objs_list = load_data_obj()
    print(configs.get('export_server', {}).get('host', ''),configs.get('export_server', {}).get('username', ''),configs.get('export_server', {}).get('password', ''))
    export_server = SSHConnector(host=configs.get('export_server', {}).get('host', ''),
                                 username=configs.get('export_server', {}).get('username', ''),
                                 password=configs.get('export_server', {}).get('password', ''))
    export_server.connect()

    with concurrent.futures.ThreadPoolExecutor(max_workers=configs.get('max_threads_number', 4)) as thread_executor:

        cmd_running_result_list = []

        for data_obj in data_objs_list:
            command = generate_commands_list(configs=configs, data_obj=data_obj)
            cmd_running_result_obj = thread_executor.submit(export_server.connection.exec_command, command)
            Logging.info(f"Start to migrate: * {data_obj} * ")
            cmd_running_result_list.append(cmd_running_result_obj)

        for future in concurrent.futures.as_completed(cmd_running_result_list, timeout=18000):

            data = future.result()
            stdin, stdout, stderr = data

            stdout_content = decode_result(stdout.read()).strip().replace('\n', ' ')
            stderr_content = decode_result(stderr.read()).strip().replace('\n', ' ')

            if stderr_content:
                Logging.error(stderr_content)
            elif stdout_content:
                Logging.info(stdout_content)
            else:
                Logging.warning("No response for running result, better to double-check the result")

    export_server.close()
    Logging.info("Complete migration, Exit now...")


def test_main():  # Test main function
    """
        Migrate data by linear model
    """
    Logging.info("The migration program is starting now -- TEST Version")

    configs = load_configs()
    data_objs_list = load_data_obj()

    export_server = SSHConnector(host=configs.get('export_server', {}).get('host', ''),
                                 username=configs.get('export_server', {}).get('username', ''),
                                 password=configs.get('export_server', {}).get('password', ''))
    export_server.connect()

    for data_obj in data_objs_list:
        command = generate_commands_list(configs=configs, data_obj=data_obj)
        stdin, stdout, stderr = export_server.connection.exec_command(command)
        Logging.info(f"Start to migrate: * {data_obj} * ")
        stdout_content = decode_result(stdout.read()).strip().replace('\n', ' ')
        stderr_content = decode_result(stderr.read()).strip().replace('\n', ' ')
        if stderr_content:
            Logging.error(stderr_content)
        elif stdout_content:
            Logging.info(stdout_content)
        else:
            Logging.info("Migration tasks has been done, please verify the result and data.")

    export_server.close()
    Logging.info("SSH connection has been closed. Exit now...")


if __name__ == '__main__':

    # test_main()  # linear mode migration and test mode

    main()  # production mode
