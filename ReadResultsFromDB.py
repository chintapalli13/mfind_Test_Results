import sqlite3


def get_connection():
    conn = sqlite3.connect('test_results')
    return conn




def main():
    c = get_connection().cursor()
    c.execute("Select message from results where build_number = '3328' and id = 'MBR-403'")
    rows = c.fetchall()
    for row  in rows:
        print (row)









if __name__ == '__main__':
    main()