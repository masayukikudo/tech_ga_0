from flask import Flask, render_template, request, redirect,jsonify, url_for, send_from_directory,send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_cors import CORS
#from flask_wtf.csrf import CSRFProtect
#from flask_wtf.csrf import generate_csrf
from datetime import datetime
import os
import pytz
import openai
from openai import OpenAI
import logging
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import re
import pandas as pd
from io import BytesIO
import xlsxwriter

class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "secret_key"
app.config['IMAGE_FOLDER'] = r'C:\Users\masay\Documents\pandas\Step3\Step3-2\newproject\backend\static\images'
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
CORS(app)
#csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

# APIキーを直接指定
api_key = "SECRET_KEY"

# APIキーを直接使用してクライアントを初期化
client = OpenAI(api_key=api_key)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    manager_comment = db.Column(db.String(300), nullable=True)
    likes = db.Column(db.Integer, default=0)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    # ユーザーがログインしていれば、投稿一覧ページを表示
    if current_user.is_authenticated:
        posts = Post.query.all()
        return render_template('index.html', posts=posts)
    # ユーザーがログインしていなければ、ログインページにリダイレクト
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=password)

        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    data = request.get_json()  # JSONデータの取得
    username = data['username']
    password = data['password']
    manager_redirect = data.get('manager_redirect', False)  # デフォルト値をFalseに設定

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        login_user(user)
        if manager_redirect:
            return jsonify({'redirectURL': '/manager'}), 200
        else:
            return jsonify({'redirectURL': '/'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/mypage')
@login_required
def mypage():
    return render_template('mypage.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        emotion = request.form.get('emotion')
        title = request.form.get('title')
        body = request.form.get('body')

        post = Post(emotion=emotion,title=title, body=body)

        db.session.add(post)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create.html')

@app.route('/check', methods=['GET'])
@login_required
def check():
    posts = Post.query.all()
    return render_template('check.html', posts=posts)

@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')

        db.session.commit()
        return redirect('/')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/manager')
@login_required
def manager():
    posts = Post.query.all()
    return render_template('manager.html', posts=posts)

@app.route('/manager/comment/<int:id>', methods=['POST'])
@login_required
def manager_comment(id):
    post = Post.query.get_or_404(id)
    post.manager_comment = request.form['manager_comment']
    db.session.commit()
    return redirect('/manager')

@app.route('/manager/update/<int:id>', methods=['GET','POST'])
@login_required
def manager_update(id):
    post = Post.query.get_or_404(id)
    post.manager_comment = request.form['manager_comment']
    db.session.commit()
    return redirect('/manager')

@app.route('/manager/comment/update/<int:post_id>', methods=['POST'])
@login_required
def update_manager_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if 'manager_comment' in request.form:
        post.manager_comment = request.form['manager_comment']
        db.session.commit()
        return jsonify({'message': 'コメントが更新されました', 'status': 'success'})
    return jsonify({'message': '更新に失敗しました', 'status': 'error'})

@app.route('/manager/like/<int:id>', methods=['POST'])
@login_required
def manager_like(id):
    post = Post.query.get_or_404(id)
    if post.likes is None:
        post.likes = 0
    post.likes += 1
    db.session.commit()
    return redirect('/manager')

@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    post_data = [{
        'id': post.id,
        'title': post.title,
        'body': post.body,
        'manager_comment': post.manager_comment,  # 経営層のコメントも含める
        'likes': post.likes,
        'created_at': post.created_at
    } for post in posts]
    return jsonify(post_data)

@app.route('/api/posts/<int:post_id>/delete', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'})

@app.route('/api/posts/<int:post_id>/update', methods=['POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    post.title = data.get('title', post.title)
    post.body = data.get('body', post.body)
    db.session.commit()
    return jsonify({'message': 'Post updated successfully', 'post': {'title': post.title, 'body': post.body}})

@app.route('/api/posts/create', methods=['POST'])
def create_post():
    data = request.get_json()
    app.logger.info(f"Received data: {data}")
    logging.info(f'Received headers: {request.headers}')
    logging.info(f'Received body: {request.get_json()}')
    new_post = Post(
        title=data['title'],
        body=data['body'],
        emotion=data['emotion'],
        created_at=datetime.now(),
        likes=0  # 初期いいね数は0
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Post created successfully'}), 201

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1  # シンプルにいいね数を増やす
    db.session.commit()
    return jsonify({'message': 'Like added successfully', 'likes': post.likes})

@app.route('/api/manager/comment/update/<int:post_id>', methods=['POST'])
def update_manager_comment_specific(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    if 'manager_comment' in data:
        post.manager_comment = data['manager_comment']
        db.session.commit()
        return jsonify({'message': 'コメントが更新されました'}), 200
    return jsonify({'error': '更新に失敗しました'}), 400

#上手くいかなかったため、"https://textmining.userlocal.jp/results/wordcloud/a309a58d-10cf-47a6-8f4a-aaae7d6e40c3"の生成結果を格納
@app.route('/api/static/images/<filename>', endpoint='get_image_static')
def get_image_static(filename):
    posts = Post.query.all()
    text = " ".join(post.title + " " + post.body for post in posts)
    text = re.sub(r'[^\w\s]', '', text)  # 単語とスペース以外を除去
    custom_stopwords = set(STOPWORDS).union({'から', 'こと', 'ため', 'それ', 'これ', 'たち', 'たくさん', '自分', 'ので'})

    # ワードクラウドの生成
    wc = WordCloud(
        background_color="white", 
        width=800, 
        height=400,
        stopwords=custom_stopwords,
        collocations=False
    ).generate(text)

    # ファイル名の生成と画像の保存
    filename = f"wordcloud_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    path = os.path.join(app.config['IMAGE_FOLDER'], filename)
    wc.to_file(path)

    return jsonify({"url": url_for('get_image', filename=filename, _external=True)})

#上手くいかなかったため、"https://textmining.userlocal.jp/results/wordcloud/a309a58d-10cf-47a6-8f4a-aaae7d6e40c3"の生成結果を格納
@app.route('/api/static/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['IMAGE_FOLDER'], filename)

@app.route('/api/chat', methods=['POST'])
def chat_with_gpt():
    user_input = request.json.get('message')  # ユーザーからの入力を取得

    # コンテキストを短縮して明確にする
    context = """
    役割: カウンセラー兼コンサルとしての役割は、社員、特にマネジメント層に属さない人々の感情や意見を理解し、経営判断に活かせるエッセンスを抽出します。感情の確認と理由の探求を行い、事実と感情の区別をつけます。
    対話の姿勢: 言い分を受け止め、寄り添い、丁寧に対応します。怒りの感情が落ち着くまで諭すことはせず、感情、主観、事実をその会話の中で深掘りし、分けられるようにします。
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": "カウンセラー兼コンサルとして精神を安定に向かわせ、正しい判断へ導く"}
            ],
            model="gpt-4",
            temperature=0.7,  # 温度パラメータを低く設定
            top_p=1.0,  # 生成の確定性を高める
        )
        full_response = response.choices[0].message.content.strip()

        # レスポンスが不完全な場合にピリオドで終了させる
        if not full_response.endswith('.'):
            full_response += '.'

        return jsonify({'response': full_response})
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/manager', methods=['POST'], endpoint='chat_with_manager')
def chat_with_gpt():
    user_input = request.json.get('message')  # ユーザーからの入力を取得

    # コンテキストを短縮して明確にする
    context = """
    役割: 経営者のアドバイザーとして、正確かつ迅速な判断支援を行います。経営者が不安や孤独を感じないよう、親身に寄り添いながらも、時間を有効に使うための端的な助言を提供します。
    対話の方法: 経営者が従業員のフィードバックや疑問にどのように対応すべきかについて助言します。提供するコメントは、経営者が迅速に意思決定を行えるよう、具体的かつ簡潔にします。問題解決のプロセスを通じて、経営者の心の安定を支援し、ポジティブな経営環境を維持することを目指します。
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": "経営者としてどのような対応をすべきか"}
            ],
            model="gpt-4",
            temperature=0.5,  # 温度パラメータを低く設定
            top_p=1.0,  # 生成の確定性を高める
        )
        full_response = response.choices[0].message.content.strip()

        # レスポンスが不完全な場合にピリオドで終了させる
        if not full_response.endswith('.'):
            full_response += '.'

        return jsonify({'response': full_response})
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export_excel', methods=['POST'])
def export_excel():
    data = request.get_json()
    # DataFrameを作成
    df = pd.DataFrame(data['tableData'])
    selected_columns = ['created_at', 'title', 'body', 'likes', 'manager_comment']
    df = df[selected_columns]
    # 日付フォーマットの変更
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y/%m/%d')

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Employee Sentiments シート
        df.to_excel(writer, sheet_name='Employee Sentiments', index=False)
        worksheet = writer.sheets['Employee Sentiments']
        worksheet.set_column('A:A', 20)  # created_at
        worksheet.set_column('B:B', 30)  # title
        worksheet.set_column('C:C', 80)  # body
        worksheet.set_column('D:D', 10)  # likes
        worksheet.set_column('E:E', 30)  # manager_comment

        # Voices Comment シート（コメントとワードクラウド画像）
        comment = data.get('voicesComment', 'No comment provided')
        # 課題②の改行処理
        comment = comment.replace('】', '】\n\n').replace('。', '。\n\n') 
        df_comments = pd.DataFrame({
            'Voices Comment': [comment]
        })
        df_comments.to_excel(writer, sheet_name='Voices Comment', index=False)
        worksheet = writer.sheets['Voices Comment']
        worksheet.set_row(1, 310)
        worksheet.write('B1', 'Word Cloud') 
        worksheet.write('A1', 'Voices Comment')
        wrap_format = writer.book.add_format({'text_wrap': True})
        worksheet.set_column('A:A', 60, wrap_format)
        worksheet.set_column('B:B', 80)

        # ワードクラウド画像を追加
        wordcloud_path = 'C:/Users/masay/Documents/pandas/Step3/Step3-2/newproject/backend/static/images/wordcloud.png'
        worksheet.insert_image('B1', wordcloud_path, {'x_scale': 0.2, 'y_scale': 0.2, 'x_offset': 15, 'y_offset': 10})

    output.seek(0)
    return send_file(output, as_attachment=True, download_name="report.xlsx")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)