import sys
from flask import escape
import tweepy
import datetime, time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'apiKey': "",
    'authDomain': "",
    'databaseURL': "",
    'projectId': "",
    'storageBucket': "",
    'messagingSenderId': "",
    'appId': "",
    'measurementId': ""
})

db = firestore.client()


####################2021/03/06　下は、処理を小分けにする関数を作成してる###############
# 認証のための関数
def auth(auth_data):
    consumer_key        = auth_data['consumerKey']
    consumer_secret     = auth_data['consumerSecret']
    access_token_key    = auth_data['accessTokenKey']
    access_token_secret = auth_data['accessTokenSecret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

# 処理を実行するか判断する関数（こんなに短いなら関数にする必要ないかも？）
def judge_run(switch):
    if switch == True:
        return True
    elif switch == False:
        return False

# 設定した上限をカウントする関数（完成してない、、）
def judge_limit(limit_number_processing, processing_count):
    if limit_number_processing > processing_count:
        processing_count += 1
        
        users_ref = db.collection('users').document('YlHpuNW8asHGmbwQyZgK').collection('processings').document('0Jf70Egna7LgzUAiasp6')
        users_ref.update({'processingCount': processing_count})

        return True
    elif processing_count >= limit_number_processing:
        return False

# firestoreから情報を取得する関数
def fetch_users_data():
    users_ref = db.collection('users')
    users = users_ref.stream()

    _users = []
    for user in users:
        _user = []
        user_info = user.to_dict()
        _user.append(user_info)

        collections_ref = users_ref.document(user.id).collections()
        for processings_ref in collections_ref:
            _processing = []
            processings = processings_ref.stream()
            for processing in processings:
                processing_info = processing.to_dict()
                _processing.append(processing_info)
            _user.append(_processing)
        _users.append(_user)
    return _users


# 設定した処理の時間に起動するための関数（完成してない、、）
def monitor_start_time(start_time_processing): # _users[1][1][0]['startTimeProcessing']　これがデータベースからとってきたスタートの時間
    get_start_time = start_time_processing.split(':')
    hour = int(get_start_time[0])
    minute = int(get_start_time[1])
    start_time = datetime.time(hour, minute)
    print(start_time)

    now = datetime.datetime.now().time()
    now_time = datetime.time(now.hour, now.minute)
    print(now_time)

    # 以下の条件分岐の計算がうまくできない。2021/03/06
    if now_time - datetime.timedelta(minutes=5) < start_time < now_time + datetime.timedelta(minutes=5):
        processing_count = 0
        print('aa')
    else:
        print('bb')



# 取得したデータからいいね処理をする関数
def favorite_with_get_data():
    # ユーザーデータの取得
    users = fetch_users_data()

    results = []
    # ユーザー全員を1人ずつ処理をかける（i=ユーザーの数）
    for i in range(len(users)):
        # データに格納されていた認証情報から認証を行い、インスタンスを取得する
        api = auth(users[1][0])
        
        conditions = []
        # 取得した処理に関するデータから１処理ずつ行う（j=処理の数）
        for j in range(len(users[i][1])):            
            processing_number       = str(j+1)
            search_word             = users[i][1][j]['searchWord']
            limit_number_processing = users[i][1][j]['limitNumberProcessing']
            processing_count        = users[i][1][j]['processingCount']
            start_time_processing   = users[i][1][j]['startTimeProcessing']
            switch                  = users[i][1][j]['switch']
            
            # 設定した処理の上限に達しているかどうかの判断を行う
            limit_judgment = judge_limit(limit_number_processing, processing_count)
            
            #switch：処理を実行するかのON/OFF設定。
            if switch and limit_judgment == True:
                search_result = api.search(q=search_word, count=1)  
                # print("配列の長さ：", len(search_result))
                if len(search_result) == 0:
                    print("配列が０でした")
                else:
                    # 取得したツイートのIDを格納
                    tweet_id = search_result[0].id
                    try:
                        time.sleep(3)
                        api.create_favorite(id=tweet_id)
                        result = 'いいねしました'
                    except tweepy.TweepError as e:
                        print(e.reason)
                        result = '失敗：' + e.reason
                print("ループ抜けてる")

                condition = {'processing_number': processing_number, 'searchWord:': search_word, 'limit_number_processing': limit_number_processing, 'result': result}
                conditions.append(condition)
            elif switch or limit_judgment == False:
                pass
        results.append({'username': users[i][0]['userName'], 'results': conditions})
    _results = str(results)
    print(_results)
    return _results





##############既に完成してる、しばらく触らない###############
def dayonpe_favorite(request):
    consumer_key = ""
    consumer_secret = ""
    access_token_key = ""
    access_token_secret = ""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    search_word = "ジヒョ"
    search_result = api.search(q=search_word, count=1)  
    print("配列の長さ：", len(search_result))
    if len(search_result) == 0:
        print("配列が０でした")
    else:
        tweet_id = search_result[0].id
        try:
            api.create_favorite(id=tweet_id)
            result = 'いいねしました'
        except tweepy.TweepError as e:
            print(e.reason)
            result = '失敗：' + e.reason
    print("ループ抜けてる")
    return result