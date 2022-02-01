import pymysql

def save_db(data):
    db = pymysql.connect(
        host="mbti-database.cttagzdge7sl.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Tpalsla118",
        database="sys",
        charset='utf8'
    )
    conn = db.cursor()

    sql = '''
    INSERT INTO t_insta_crawler(mbti, short_code, media_id, content_text, published_at, tag_list, user_id, user_name, like_count)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''

    conn.executemany(sql, data)
    db.commit()
    conn.close()
