import mysql.connector

#search the users table for an existing entry by discord_id
def select_user_by_discord_id():
    return "SELECT user_id FROM users WHERE discord_id = %s"

#search the reasons table for an existing entry by name
def select_reason_by_name():
    return "SELECT reason_id FROM reason WHERE name = %s"

#search the punish table for an existing entry by name
def select_punish_by_name():
    return "SELECT punish_id FROM punish WHERE name = %s"

#insert a user into the users table
def insert_user():
    return "INSERT INTO users (username, discord_id) VALUES (%s, %s)"

#insert a reason into the reasons table
def insert_reason():
    return "INSERT INTO reason (name) VALUES (%s)"

#insert a punishment into the punish table
def insert_punish():
    return "INSERT INTO punish (name) VALUES (%s)"

#insert a log into the log table
def insert_log():
    return "INSERT INTO log (user_id, reason_id, punish_id) VALUES (%s, %s, %s)"

#populate log
def create_log(db_cursor, db_connection, discord_id, reason_name, punish_name):
    try:
        user_id_query = select_user_by_discord_id()
        reason_id_query = select_reason_by_name()
        punish_id_query = select_punish_by_name()

        # Fetch IDs from the respective tables
        db_cursor.execute(user_id_query, (discord_id,))
        user_id = db_cursor.fetchone()
        print(user_id)

        db_cursor.execute(reason_id_query, (reason_name,))
        reason_id = db_cursor.fetchone()
        print(reason_id)

        db_cursor.execute(punish_id_query, (punish_name,))
        punish_id = db_cursor.fetchone()
        print(punish_id)

        if user_id and reason_id and punish_id:
            # Insert the log entry into the log table
            insert_log_query = insert_log()
            values = (user_id[0], reason_id[0], punish_id[0])
            db_cursor.execute(insert_log_query, values)
            db_connection.commit()
            return True
        else:
            return False

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return False