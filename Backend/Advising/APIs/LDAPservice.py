from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import os
from dotenv import load_dotenv
# load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
load_dotenv()

LDAP_HOST = "dirsrv"
# 3389 for connection through containers 
# 7389 for connection through host
LDAP_PORT = 3389
LDAP_USER = "cn=Directory Manager"
LDAP_PASS = os.getenv("DS_DM_PASSWORD")
# BASE_DN = "dc=UAFS,dc=COM"
BASE_DN = "cn=Users,cn=Person,dc=UAFS,dc=COM"
LDAP_URL = f"ldap://{LDAP_HOST}:{LDAP_PORT}"

def _connect():
    print("Connecting to LDAP:", LDAP_URL)
    print("Using admin DN:", LDAP_USER)
    if not LDAP_PASS:
        print("LDAP WARNING: DS_DM_PASSWORD is not set. LDAP operations are disabled.")
        return None

    try:
        server = Server(LDAP_URL, get_info=ALL)
        conn = Connection(server, LDAP_USER, LDAP_PASS, auto_bind=True)
        print("LDAP result:", conn.result)
        return conn
    except Exception as ex:
        print("LDAP ERROR: Failed to bind:", ex)
        return None

def addUser(email, firstname, lastname):
    conn = _connect()
    if conn is None:
        return False

    dn = f"uid={email},{BASE_DN}"

    try:
        result = conn.add(
            dn,
            ['inetorgperson', 'inetuser'],
            {
                'uid': email,
                'givenName': firstname,
                'sn': lastname,
                'cn': f"{firstname} {lastname}",
                'userPassword': 'password123'
            }
        )

        if not result:
            print("LDAP add error:", conn.result)
            return False

    finally:
        conn.unbind()

    return True

def deleteUser(email):
    conn = _connect()
    if conn is None:
        return False

    dn = f"uid={email},{BASE_DN}"

    try:
        result = conn.delete(dn)
        if not result:
            print("LDAP delete error:", conn.result)
            return False

    finally:
        conn.unbind()

    return True

def updateUser(oldEmail, newEmail, firstname, lastname):
    conn = _connect()
    if conn is None:
        return False

    old_dn = f"uid={oldEmail},{BASE_DN}"
    new_dn = f"uid={newEmail},{BASE_DN}"

    try:
        if oldEmail != newEmail:
            rename_ok = conn.modify_dn(old_dn, f"uid={newEmail}", delete_old_rdn=True)
            if not rename_ok:
                print("LDAP rename error:", conn.result)
                return False

        updateOk = conn.modify(
            new_dn,
            {
                "uid": [(MODIFY_REPLACE, [newEmail])],
                "cn": [(MODIFY_REPLACE, [f"{firstname} {lastname}"])],
                "givenName": [(MODIFY_REPLACE, [firstname])],
                "sn": [(MODIFY_REPLACE, [lastname])]
            }
        )

        if not update_ok:
            print("LDAP update error:", conn.result)
            return False

    finally:
        conn.unbind()

    return True