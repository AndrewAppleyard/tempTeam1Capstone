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
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from extensions import jwt

bp = Blueprint('TransferAPI', __name__, url_prefix="/Transfer")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

LDAP_HOST = "dirsrv"
LDAP_PORT = 3389
LDAP_USER = "cn=Directory Manager"
LDAP_PASS = "andrewandrew"
BASE_DN = "dc=UAFS,dc=COM"

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
            if "UAFS_ADMINS" in group:
                token = create_access_token(identity=username, additional_claims={"Role":"Admin"})
                return jsonify({'message':'User authenticated successfully!', "Token":token}), 200
            elif "UAFS_STUDENTS" in group:
                token = create_access_token(identity=username, additional_claims={"Role":"Student"})
                return jsonify({'message':'User authenticated successfully!', "Token":token}), 200
            elif "UAFS_ADVISORS" in group:
                token = create_access_token(identity=username, additional_claims={"Role":"Advisor"})
                return jsonify({'message':'User authenticated successfully!', "Token":token}), 200
            else:
                print("User found but user is assigned to a group we aren't handling.")
                return jsonify({"message":"User found but user is assigned to a group we aren't handling."}), 401
            
    except Exception as e:
        print("error", e)