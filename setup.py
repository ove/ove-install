from __future__ import print_function

import re
import os
import sys
import json

from distutils.spawn import find_executable

SQL_DB_SERVER = "ovehub-ove-asset-db"
SQL_DB_PORT = "3306"
SQL_DB_DATABASE = "AssetDatabase"
SQL_DB_USER = "assetManager"
SQL_DB_PASSWORD = "assetManager"

S3_SERVER = "ovehub-ove-asset-storage"
S3_PORT = "9000"
S3_ACCESS_KEY = "MINIO_ACCESS_KEY"
S3_SECRET_KEY = "MINIO_SECRET_KEY"


# On Python 2.7, input() evaluates what the user types, and raw_input() simply returns it
# On Python 3, input() returns it, and there is no raw_input() function
try:
    input = raw_input
except NameError:
    pass


# On Python 2.7, failing to parse JSON throws a ValueError; on Python 3 it throws json.decoder.JSONDecodeError
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def bundle_dir():
    return sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))


def check_dependencies():
    if find_executable("docker") is None:
        print("WARN: docker is required to run the system")
        print("For install instructions, visit https://docs.docker.com/install/")

    if find_executable("docker-compose") is None:
        print("WARN: docker-compose is required to run the generated configs")
        print("For install instructions, visit https://docs.docker.com/compose/install/")


def get_default_ip():
    try:
        from netifaces import ifaddresses, gateways, AF_INET
    except:
        print("WARN: Failed to import netifaces, so cannot determine default ip")
        return ""

    try:
        default_iface = gateways()['default'][AF_INET][1]
        addr = ifaddresses(default_iface)
        return addr[AF_INET][0]['addr']
    except:
        print("WARN: Failed to determine the default ip")
        return ""


def read_var(message, default_value, note=None):
    if note is not None:
        print("NOTE:", note)
    result = input("%s (default: %s): " % (message, default_value))
    result = result.strip()
    result = result if len(result) > 0 else default_value

    print("\tINFO: %s = %s" % (message, result))

    return result


def read_flag(message, default_value, note=None):
    if note is not None:
        print("NOTE:", note)
    result = input("%s (default: %s)? " % (message, default_value))
    result = result.strip()
    result = result if len(result) > 0 else default_value

    result = True if result.lower() in ('yes', 'true', 't', 'y', 'ye', '1') else False

    print("\tINFO: %s = %s" % (message, 'yes' if result else 'no'))

    return result


def exit_msg():
    print("")
    input("Press Enter to exit")


def intro_msg(params):
    print("This setup script will generate docker-compose scripts using the following versions:")
    print("\tNOTE: If these versions differ from the latest available, please use the latest setup generator.")
    print("")
    print("\t OVE Version: ", params['OVE_VERSION'])
    print("\t OVE Apps Version: ", params['OVE_APPS_VERSION'])
    print("\t TUORIS Version: ", params['TUORIS_VERSION'])
    print("\t Asset Manager Version: ", params['ASSET_MANAGER_VERSION'])
    print("\t Database Version: ", params['SQL_DB_VERSION'])
    print("")


def outro_msg(proceed):
    print("")
    print("Thank you for using this setup tool!")
    if proceed:
        print("")
        print("---")
        print("Your docker-compose configs have been generated. You can execute them directly by using:")
        print("")
        print("\t docker-compose -f docker-compose.setup.ove.yml up -d")
        print("\t docker-compose -f docker-compose.setup.assets.yml up -d")
        print("")
        print("NOTE: -d flag runs the docker commands in detached mode")
        print("---")


def load_version_numbers(release):
    try:
        bundle_wd = bundle_dir()
        with open(os.path.join(bundle_wd, "versions.json")) as fp:
            versions = json.load(fp)
        return versions['releases'][release]
    except KeyError:
        return None
    except JSONDecodeError:
        print("ERROR: Unable to parse versions.json file")
        exit_msg()
        sys.exit()
    except:
        print("Error: Unable to read versions.json file")
        exit_msg()
        sys.exit()


def get_stable_version():
    try:
        bundle_wd = bundle_dir()
        with open(os.path.join(bundle_wd, "versions.json")) as fp:
            versions = json.load(fp)
        return versions['stable']
    except JSONDecodeError:
        print("ERROR: Unable to parse versions.json file")
        exit_msg()
        sys.exit()
    except:
        print("Error: Unable to read versions.json file")
        exit_msg()
        sys.exit()


def read_script_params():
    print("")
    print("General settings")
    print("")

    ip = ""
    while not ip:
        ip = read_var("Machine hostname or ip address", get_default_ip())

    stable_version = get_stable_version()
    use_stable = read_flag("Use 'stable' version", "yes")
    if use_stable:
        versions = load_version_numbers(stable_version)
    else:
        use_latest = read_flag("Use 'latest' version", "yes")
        if use_latest:
            versions = load_version_numbers('latest')
        else:
            version = ""
            while load_version_numbers(version) is None:
                version = read_var("Version number (x.y.z)", stable_version)
            versions = load_version_numbers(version)

    ove_version = versions['ove']
    ove_apps_version = versions['ove-apps']
    tuoris_version = versions['tuoris']
    asset_manager_version = versions['asset-manager']
    sql_version = versions['mariaDB']

    defaults = read_flag("Use default settings", "yes")
    if defaults:
        sql_enabled = True
        sql_server = SQL_DB_SERVER
        sql_external_port = SQL_DB_PORT
        sql_port = SQL_DB_PORT
        sql_db = SQL_DB_DATABASE
        sql_user = SQL_DB_USER
        sql_passwords = SQL_DB_PASSWORD

        s3_enabled = True
        s3_server = S3_SERVER
        s3_external_port = S3_PORT
        s3_port = S3_PORT
        s3_access_key = S3_ACCESS_KEY
        s3_secret_key = S3_SECRET_KEY
    else:
        print("")
        print("OVE Asset Manager setup")
        print("")
        sql_enabled = read_flag("Use internal SQL DB", "yes")
        if sql_enabled:
            sql_server = SQL_DB_SERVER
            sql_external_port = read_var("SQL DB external port", SQL_DB_PORT)
            sql_port = SQL_DB_PORT
        else:
            sql_server = read_var("SQL DB server", ip)
            sql_external_port = ""
            sql_port = read_var("SQL DB port", SQL_DB_PORT)

        sql_db = read_var("SQL DB Name", SQL_DB_DATABASE)
        sql_user = read_var("SQL DB username", SQL_DB_USER)
        sql_passwords = read_var("SQL DB password", SQL_DB_PASSWORD)

        s3_enabled = read_flag("Use internal S3 storage", "yes")
        if s3_enabled:
            s3_server = S3_SERVER
            s3_external_port = read_var("S3 external port", S3_PORT)
            s3_port = S3_PORT
        else:
            s3_server = read_var("S3 server", ip)
            s3_external_port = ""
            s3_port = read_var("S3 server port", S3_PORT)

        s3_access_key = read_var("S3 Access key", S3_ACCESS_KEY)
        s3_secret_key = read_var("S3 Secret key", S3_SECRET_KEY)

    return {
        'PUBLIC_HOSTNAME': ip,

        'OVE_VERSION': ove_version,
        'OVE_APPS_VERSION': ove_apps_version,
        'TUORIS_VERSION': tuoris_version,

        'ASSET_MANAGER_VERSION': asset_manager_version,

        'SQL_DB_ENABLED': sql_enabled,
        'SQL_DB_SERVER': sql_server,
        'SQL_DB_PORT': sql_port,
        'SQL_DB_EXT_PORT': sql_external_port,
        'SQL_DB_VERSION': sql_version,
        'SQL_DB_NAME': sql_db,
        'SQL_DB_USER': sql_user,
        'SQL_DB_PASSWORD': sql_passwords,

        'S3_ENABLED': s3_enabled,
        'S3_SERVER': s3_server,
        'S3_EXT_PORT': s3_external_port,
        'S3_PORT': s3_port,
        'S3_ACCESS_KEY': s3_access_key,
        'S3_SECRET_KEY': s3_secret_key,
    }


def generate_scripts(input_filename, output_filename, params):
    # todo; some file validation here
    with open(input_filename, mode="r") as fin:
        content = fin.read()

    for k, v in params.items():
        content = content.replace("${%s}" % k, str(v))
        content = content.replace("$%s" % k, str(v))

    if not params['SQL_DB_ENABLED']:
        content = re.sub(pattern=r"[ ]*## BEGIN SQL DB CONFIG ##.*## END SQL DB CONFIG ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)
        content = re.sub(pattern=r"[ ]*## BEGIN SQL DB DEPENDENCY ##.*## END SQL DB DEPENDENCY ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)
        content = re.sub(pattern=r"[ ]*## BEGIN SQL DB STORAGE ##.*## END SQL DB STORAGE ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)

    if not params['S3_ENABLED']:
        content = re.sub(pattern=r"[ ]*## BEGIN S3 CONFIG ##.*## END S3 CONFIG ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)
        content = re.sub(pattern=r"[ ]*## BEGIN S3 STORAGE ##.*## END S3 STORAGE ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)

    if not params['SQL_DB_ENABLED'] and not params['S3_ENABLED']:
        content = re.sub(pattern=r"[ ]*## BEGIN STORAGE ##.*## END STORAGE ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)

    # cleanup "special comments"
    content = re.sub(pattern=r"[ ]*##.*##[ ]*\n?", repl="", string=content)

    with open(output_filename, mode="w") as fout:
        fout.write(content)

    print("Generated new docker-compose config file in ", output_filename)


def main():
    check_dependencies()
    bundle_wd = bundle_dir()

    params = read_script_params()
    intro_msg(params)

    proceed = read_flag("Accept and proceed", "yes")

    print("")

    if proceed:
        generate_scripts(params=params,
                         input_filename=os.path.join(bundle_wd, "templates", "docker-compose.ove.yml"),
                         output_filename=os.path.join(os.getcwd(), "docker-compose.setup.ove.yml"))
        generate_scripts(params=params,
                         input_filename=os.path.join(bundle_wd, "templates", "docker-compose.assets.yml"),
                         output_filename=os.path.join(os.getcwd(), "docker-compose.setup.assets.yml"))

    outro_msg(proceed)
    exit_msg()


if __name__ == "__main__":
    main()
