from datetime import datetime
import pandas as pd
import pickle
import json

import db_conn


def str_cleaner(text):
    if not isinstance(text, str):
        return ""
    text = text.replace('\n', '').replace('\r', '').replace('\t', '')
    return text


def parse_tag(text):
    t = text.split(' ')[0]
    t = str_cleaner(t)
    return t


def parse_section_media(media_list, input_keyword):
    result = []
    for m in media_list:
        section_media_list = m.get('layout_content').get('medias')
        for media in section_media_list:
            # TODO media 객체도 리턴하여 RAW 데이터를 저장할 수 있도록 해야 함
            sect = media.get('media')
            user = sect.get('user')
            short_code = sect.get('code')
            sect_media = sect.get('caption')
            like_cnt = sect.get('like_count', 0)
            media_time = sect_media.get('created_at') if sect_media is not None else sect.get('taken_at')
            try:
                published_at = datetime.fromtimestamp(int(media_time))
            except Exception as e:
                published_at = None
            media_id = sect_media.get('media_id') if sect_media is not None else sect.get('pk')
            content = sect_media.get('text', "") if sect_media is not None else sect.get('caption', "")
            if content is None:
                tag_list = []
            else:
                tag_list = list(map(parse_tag, [x for x in content.split("#")
                                                if content[content.find(x)-1] == '#' and content.find(x) != 0]))
            item = {'short_code': short_code, 'media_id': media_id, 'content': str_cleaner(content),
                    'published_at': published_at, 'tag_list': tag_list, 'user_id': user.get('pk'),
                    'user_name': user.get('username'), 'like_count': like_cnt
                    }
            item_list = [input_keyword, short_code,media_id, str_cleaner(content), published_at, str(tag_list), user.get('pk'),user.get('username'),like_cnt]
            result.append(item_list)
    return result


def parse_main(file_name, input_keyword):
    # with open(f'{file_name}.pickle', 'rb') as f:
    #     data = pickle.load(f)

    result = []
    result_df = pd.DataFrame()
    for d in file_name:
        if d['network_id'] is None:
            media_list = d['item'].get('data').get('recent').get('sections')
        else:
            body = json.loads(d['item']['body'])
            media_list = body.get('sections')

        result.extend(parse_section_media(media_list, input_keyword)) # result = list[{},{},{}]
    db_conn.save_db(result)
    # return df


if __name__ == '__main__':
    result_df = pd.DataFrame()
    import pprint

    # for t in ['estj', 'enfp', 'infp', 'istj', 'mbti', 'esfp']:
    #     result_df = result_df.append(parse_main(f"{t}_res"))
    # result_df = result_df.drop_duplicates(['short_code'], keep='first')
    #
    # with open('mbti_result.pickle', 'wb') as f:
    #     pickle.dump(result_df, f, pickle.HIGHEST_PROTOCOL)


