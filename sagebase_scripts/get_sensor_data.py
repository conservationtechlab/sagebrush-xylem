import psycopg
import json
import os

def get_secrets(fname='secrets.json'):

    assert os.path.exists(fname), 'check secrets filepath'

    with open(fname, 'r') as f:
        return json.load(f)

def connect_to_db(dict):

    try:
        conn = psycopg.connect(
            dbname=dict['db'],
            user=dict['user'],
            password=dict['password'],
            host=dict['host'],
            port=dict['port'],
        )
        print("Connection OK")
    except Exception as e:
        print("Connection failed: ", e)

    return conn

if __name__=='__main__':
    secrets = get_secrets()
    connection = connect_to_db(secrets)

    with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:

        cur.execute("""
            SELECT * FROM v_field_sensor_lat_long_last_dt
        """)


        rows = cur.fetchall()

#        colnames = [desc[0] for desc in cur.description]

#        print(colnames)
        data = {}
        '''
        for deployement_id, recorded_at, temperature in rows:
            data[deployment_id] = {
                'time_stamp': recorded_at,
                'temperature': str(temperature)
            }

        '''

        for row in rows:
            deployment_id = row['deployment_id']
            data[deployment_id] = {
                'time_stamp': str(row['recorded_at']),
                'temperature': row['temperature']
            }

        with open('latest_sensors.json', 'w') as f:
            json.dump(data, f, indent=2)

        print('JSON export complete!')
