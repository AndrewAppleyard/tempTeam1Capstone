from flask import Blueprint, Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
import os, sys
from ldap3 import Server, Connection, ALL, SUBTREE
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, \
create_refresh_token, set_access_cookies, set_refresh_cookies, \
get_jwt_identity, unset_jwt_cookies
from extensions import jwt
from Advising.APIs import URL

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

from UserClasses import Student, Advisor, Admin

path = os.path.abspath(__file__)
directory = os.path.dirname(path)
databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")

engine = create_engine(databaseURL)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

bp = Blueprint('TransferAPI', __name__, url_prefix="/Transfer")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

LDAP_HOST = "dirsrv"
# 3389 for connection through containers 
# 7389 for connection through host
LDAP_PORT = 3389
LDAP_USER = "cn=Directory Manager"
LDAP_PASS = "andrewandrew"
BASE_DN = "dc=UAFS,dc=COM"

def lookup_user_id(username: str, group: str):
    try:
        with Session(engine) as session:
            if "UAFS_STUDENTS" in group:
                student = session.query(Student.StudentMap).filter(Student.StudentMap.email == username).first()
                return student.studentid if student else None
            if "UAFS_ADVISORS" in group:
                advisor = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.email == username).first()
                return advisor.advisorid if advisor else None
            if "UAFS_ADMINS" in group:
                admin = session.query(Admin.AdminMap).filter(Admin.AdminMap.email == username).first()
                return admin.adminid if admin else None
    except Exception:
        traceback.print_exc()
    return None

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    
    print(f"Connecting on {LDAP_HOST}:{LDAP_PORT}")

    user_dn = f"uid={username},cn=Users,cn=Person,{BASE_DN}"

    
    try:
        server = Server(LDAP_HOST, port=LDAP_PORT, get_info=ALL)
        conn = Connection(server, user=LDAP_USER, password=LDAP_PASS, auto_bind=True)

        print("Connection successful")

        conn.search(search_base=BASE_DN, search_filter=f"(uid={username})", search_scope=SUBTREE, attributes=["dn"])


        if not conn.entries:
            print("User not found.")
            return jsonify({"message":"User not found."}), 401
        else:
            
            try:
                user_conn = Connection(server, user=user_dn, password=password, auto_bind=True)
                print(f"Authentication successful for {username}")
                user_conn.unbind()
            except Exception:
                print(f"Authentication failed: Incorrect password for {username}")
                return jsonify({"message":"Authentication failed: Incorrect password for {username}"}), 401
            
            user_dn = conn.entries[0].entry_dn
            conn.search(search_base=BASE_DN, search_filter=f"(member={user_dn})", search_scope=SUBTREE,attributes=["cn"])

            if not conn.entries:
                print("User found but user isn't assigned to any groups.")
                return jsonify({"message":"User found but user isn't assigned to any groups."}), 401
            else:
                group = conn.entries[0].cn.value
                print(f"The user {username} is in group {group}")
            
            conn.unbind()
            user_id = lookup_user_id(username, group)

            if "UAFS_ADMINS" in group:
                claims = {"Role":"UAFS_ADMINS"}
                if user_id:
                    claims["UserID"] = user_id
                access_token = create_access_token(identity=username, additional_claims=claims)
                refresh_token = create_refresh_token(identity=username, additional_claims=claims)
                resp = jsonify({"login": True, "Role": "UAFS_ADMINS", "UserID": user_id, "Email": username})
                set_access_cookies(resp, access_token)
                set_refresh_cookies(resp, refresh_token)
                return resp, 200
            elif "UAFS_STUDENTS" in group:
                claims = {"Role":"UAFS_STUDENTS"}
                if user_id:
                    claims["UserID"] = user_id
                access_token = create_access_token(identity=username, additional_claims=claims)
                refresh_token = create_refresh_token(identity=username, additional_claims=claims)
                resp = jsonify({"login": True, "Role": "UAFS_STUDENTS", "UserID": user_id, "Email": username})
                set_access_cookies(resp, access_token)
                set_refresh_cookies(resp, refresh_token)
                return resp, 200
            elif "UAFS_ADVISORS" in group:
                claims = {"Role":"UAFS_ADVISORS"}
                if user_id:
                    claims["UserID"] = user_id
                access_token = create_access_token(identity=username, additional_claims=claims)
                refresh_token = create_refresh_token(identity=username, additional_claims=claims)
                resp = jsonify({"login": True, "Role": "UAFS_ADVISORS", "UserID": user_id, "Email": username})
                set_access_cookies(resp, access_token)
                set_refresh_cookies(resp, refresh_token)
                return resp, 200
            else:
                print("User found but user is assigned to a group we aren't handling.")
                return jsonify({"message":"User found but user is assigned to a group we aren't handling."}), 401
            
    except Exception as e:
        print("error", e)

@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    claims = {"Role": get_jwt().get("Role")}
    if get_jwt().get("UserID"):
        claims["UserID"] = get_jwt().get("UserID")
    new_access = create_access_token(identity=identity, additional_claims=claims)
    resp = jsonify({"refresh": True, "Role": claims.get("Role"), "UserID": claims.get("UserID"), "Email": identity})
    set_access_cookies(resp, new_access)
    return resp

@bp.route("/logout", methods=["POST"])
def logout():
    resp = jsonify({"logout": True})
    unset_jwt_cookies(resp)
    return resp