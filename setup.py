#!/usr/bin/env python

from __future__ import print_function

import errno
import json
import os
import re
import sys
from distutils.spawn import find_executable

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


def generate_jwt_secret():
    try:
        import secrets
        return secrets.token_urlsafe()
    except ImportError:
        import random
        import string
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(10))

OPENVIDU_SECRET = "MY_SECRET"

AM_STORE_NAME = "default"

S3_SERVER = "ovehub-ove-asset-storage"
S3_PORT = "9000"
S3_ACCESS_KEY = "MINIO_ACCESS_KEY"
S3_SECRET_KEY = "MINIO_SECRET_KEY"

MONGO_HOST = "ovehub-ove-asset-mongo"
MONGO_PORT = 27017
MONGO_USER = "user"
MONGO_PASSWORD = "password"
MONGO_DB = "db"
MONGO_COLLECTION = "auth"
MONGO_AUTH_MECHANISM = "SCRAM-SHA-256"
JWT_SECRET = generate_jwt_secret()


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
    print("\t OVE Services Version: ", params['OVE_SERVICES_VERSION'])
    print("\t OVE UI Version: ", params['OVE_UI_VERSION'])
    print("\t Tuoris Version: ", params['TUORIS_VERSION'])
    print("\t OpenVidu Version: ", params['OPENVIDU_VERSION'])
    if params['ASSET_MANAGER_VERSION']:
        print("\t Asset Manager Version: ", params['ASSET_MANAGER_VERSION'])
    print("")


def outro_msg(proceed, params):
    print("")
    print("Thank you for using this setup tool!")
    if proceed:
        print("")
        print("---")
        print("Your docker-compose configs have been generated. You can execute them directly by using:")
        print("")
        print("\t docker-compose -f docker-compose.setup.ove.yml up -d")
        if params['ASSET_MANAGER_VERSION']:
            print("\t docker-compose -f docker-compose.setup.am.yml up -d")
            print("\t NOTE: If you copy the compose files to another machine, please also copy the generated files in the 'config/' directory")
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
    ove_services_version = versions['ove-services']
    ove_ui_version = versions['ove-ui']
    tuoris_version = versions['tuoris']
    openvidu_version = versions['openvidu']
    asset_manager_version = versions.get('asset-manager', None)

    # defaults
    am_store_name = None

    s3_enabled = False
    s3_server = None
    s3_external_ip = None
    s3_external_port = None
    s3_port = None
    s3_access_key = None
    s3_secret_key = None

    mongo_enabled = False
    mongo_host = None
    mongo_port = None
    mongo_user = None
    mongo_password = None
    mongo_db = None
    mongo_collection = None
    mongo_auth_mechanism = None
    jwt_secret = None

    defaults = read_flag("Use default settings", "yes")

    if defaults:
        get_val = lambda prompt, default_val: default_val
        get_flag = lambda prompt, default_val: default_val
    else:
        get_val = read_var
        get_flag = read_flag

    print("")
    print("OVE setup")
    print("")

    openvidu_secret = get_val("OpenVidu Secret", OPENVIDU_SECRET)

    if asset_manager_version:
        print("")
        print("OVE Asset Manager setup")
        print("")

        am_store_name = get_val("Asset Manager default store name", AM_STORE_NAME)

        s3_enabled = get_flag("Add Minio instance (S3 store) to docker-compose file", "yes")
        if s3_enabled:
            s3_server = S3_SERVER
            s3_port = S3_PORT
            s3_external_ip = get_val("S3 external ip or hostname", ip)
            s3_external_port = get_val("S3 external port", S3_PORT)
        else:
            s3_server = get_val("S3 server", ip)
            s3_port = get_val("S3 server port", S3_PORT)
            s3_external_ip = s3_server
            s3_external_port = s3_port

        s3_access_key = get_val("S3 Access key", S3_ACCESS_KEY)
        s3_secret_key = get_val("S3 Secret key", S3_SECRET_KEY)

        mongo_enabled = get_flag("Add MongoDB instance to docker-compose file", "yes")
        if mongo_enabled:
            mongo_host = MONGO_HOST
            mongo_port = get_val("MongoDB external port", MONGO_PORT)
        else:
            mongo_host = get_val("MongoDB hostname", MONGO_PORT)
            mongo_port = get_val("MongoDB port", MONGO_PORT)

        mongo_user = get_val("MongoDB username", MONGO_USER)
        mongo_password = get_val("MongoDB password", MONGO_PASSWORD)
        mongo_db = get_val("MongoDB database name", MONGO_DB)
        mongo_collection = get_val("MongoDB collection name", MONGO_COLLECTION)
        mongo_auth_mechanism = get_val("MongoDB auth mechanism", MONGO_AUTH_MECHANISM)

        jwt_secret = get_val("MongoDB auth mechanism", JWT_SECRET)

    return {
        'PUBLIC_HOSTNAME': ip,

        'OVE_VERSION': ove_version,
        'OVE_APPS_VERSION': ove_apps_version,
        'OVE_SERVICES_VERSION': ove_services_version,
        'OVE_UI_VERSION': ove_ui_version,
        'TUORIS_VERSION': tuoris_version,
        'OPENVIDU_VERSION': openvidu_version,
        'OPENVIDU_SECRET': openvidu_secret,

        'ASSET_MANAGER_VERSION': asset_manager_version,

        'AM_STORE_NAME': am_store_name,

        'S3_ENABLED': s3_enabled,
        'S3_SERVER': s3_server,
        'S3_PORT': s3_port,
        'S3_EXT_PORT': s3_external_port,
        'S3_EXT_IP': s3_external_ip,
        'S3_ACCESS_KEY': s3_access_key,
        'S3_SECRET_KEY': s3_secret_key,

        'MONGO_ENABLED': mongo_enabled,
        'MONGO_HOST': mongo_host,
        'MONGO_PORT': mongo_port,
        'MONGO_USER': mongo_user,
        'MONGO_PASSWORD': mongo_password,
        'MONGO_DB': mongo_db,
        'MONGO_COLLECTION': mongo_collection,
        'MONGO_AUTH_MECHANISM': mongo_auth_mechanism,

        'JWT_SECRET': jwt_secret
    }


def generate_scripts(input_filename, output_filename, params):
    # todo; some file validation here
    with open(input_filename, mode="r") as fin:
        content = fin.read()

    for k, v in params.items():
        content = content.replace("${%s}" % k, str(v))
        content = content.replace("$%s" % k, str(v))

    if not params['S3_ENABLED']:
        content = re.sub(pattern=r"[ ]*## BEGIN S3 CONFIG ##.*## END S3 CONFIG ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)
        content = re.sub(pattern=r"[ ]*## BEGIN S3 STORAGE ##.*## END S3 STORAGE ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)

    if not params['MONGO_ENABLED']:
        content = re.sub(pattern=r"[ ]*## BEGIN MONGO CONFIG ##.*## END MONGO CONFIG ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)
        content = re.sub(pattern=r"[ ]*## BEGIN MONGO STORAGE ##.*## END MONGO STORAGE ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)

    if not params['MONGO_ENABLED'] and not params['S3_ENABLED']:
        content = re.sub(pattern=r"[ ]*## BEGIN STORAGE ##.*## END STORAGE ##[ ]*\n?",
                         repl="", string=content, flags=re.MULTILINE | re.DOTALL)

    # cleanup "special comments"
    content = re.sub(pattern=r"[ ]*##.*##[ ]*\n?", repl="", string=content)

    output_path = os.path.dirname(output_filename)
    try:
        os.makedirs(output_path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(output_path):
            pass
        else:
            raise

    with open(output_filename, mode="w") as fout:
        fout.write(content)

    print("Generated new config file in ", output_filename)


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
                         input_filename=os.path.join(bundle_wd, "templates", "config", "Spaces.json"),
                         output_filename=os.path.join(os.getcwd(), "config", "Spaces.json"))
        generate_scripts(params=params,
                         input_filename=os.path.join(bundle_wd, "templates", "config", "default.conf"),
                         output_filename=os.path.join(os.getcwd(), "config", "default.conf"))

        if params['ASSET_MANAGER_VERSION']:
            generate_scripts(params=params,
                             input_filename=os.path.join(bundle_wd, "templates", "docker-compose.am.yml"),
                             output_filename=os.path.join(os.getcwd(), "docker-compose.setup.am.yml"))
            generate_scripts(params=params,
                             input_filename=os.path.join(bundle_wd, "templates", "config", "credentials.template.json"),
                             output_filename=os.path.join(os.getcwd(), "config", "credentials.json"))
            generate_scripts(params=params,
                             input_filename=os.path.join(bundle_wd, "templates", "config", "init_mongo.js"),
                             output_filename=os.path.join(os.getcwd(), "config", "init_mongo.js"))
            generate_scripts(params=params,
                             input_filename=os.path.join(bundle_wd, "templates", "config", "auth.template.json"),
                             output_filename=os.path.join(os.getcwd(), "config", "auth.json"))
            generate_scripts(params=params,
                             input_filename=os.path.join(bundle_wd, "templates", "config", "whitelist.template.json"),
                             output_filename=os.path.join(os.getcwd(), "config", "whitelist.json"))
            generate_scripts(params=params,
                             input_filename=os.path.join(bundle_wd, "templates", "config", "worker.template.json"),
                             output_filename=os.path.join(os.getcwd(), "config", "worker.json"))

    outro_msg(proceed, params)
    exit_msg()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # ignore
        pass
