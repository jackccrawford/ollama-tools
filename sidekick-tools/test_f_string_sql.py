#!/usr/bin/env python3
"""
Test file for f-string SQL injection patterns
This should trigger the enhanced Security Auditor patterns
"""

import sqlite3

def vulnerable_query(user_id):
    # This should be detected by enhanced f-string patterns
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def another_vulnerability(table_name, condition):
    # This should also be detected
    sql = f"INSERT INTO {table_name} VALUES ({condition})"
    return sql

def update_vulnerability(user_data, user_id):
    # And this one too
    update_sql = f"UPDATE users SET data = '{user_data}' WHERE id = {user_id}"
    return update_sql

def delete_vulnerability(user_id):
    # Final test case
    delete_sql = f"DELETE FROM users WHERE id = {user_id}"
    return delete_sql