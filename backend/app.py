from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from openai import OpenAI
import pandas as pd
from io import BytesIO
import xlsxwriter

# Flaskアプリケーションの設定
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "secret_key"
app.config['IMAGE_FOLDER'] = r'C:\Users\masay\Documents\pandas\Step3\Step3-2\newproject\backend\static\images'
db = SQLAlchemy(app)
CORS(app)

# OpenAI APIキーの設定
client = OpenAI(api_key="YOUR_SECRET_KEY")

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    manager_comment = db.Column(db.String(300), nullable=True)
    likes = db.Column(db.Integer, default=0)

@app.route('/api/chat', methods=['POST'])
def chat_with_gpt():
    user_input = request.json.get('message')  # ユーザーからの入力を取得

    context = """
    役割: カウンセラー兼コンサルとしての役割は、社員、特にマネジメント層に属さない人々の感情や意見を理解し、経営判断に活かせるエッセンスを抽出します。感情の確認と理由の探求を行い、事実と感情の区別をつけます。
    対話の姿勢: 言い分を受け止め、寄り添い、丁寧に対応します。怒りの感情が落ち着くまで諭すことはせず、感情、主観、事実をその会話の中で深掘りし、分けられるようにします。
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7  # 温度パラメータを低く設定
        )

        full_response = response.choices[0].message.content.strip()
        if not full_response.endswith('.'):
            full_response += '.'

        return jsonify({'response': full_response})
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_excel', methods=['POST'])
def export_excel():
    data = request.get_json()
    df = pd.DataFrame(data['tableData'])
    selected_columns = ['created_at', 'title', 'body', 'likes', 'manager_comment']
    df = df[selected_columns]
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y/%m/%d')

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Employee Sentiments', index=False)
        worksheet = writer.sheets['Employee Sentiments']
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 80)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 30)

        comment = data.get('voicesComment', 'No comment provided')
        comment = comment.replace('】', '】\n\n').replace('。', '。\n\n')
        df_comments = pd.DataFrame({'Voices Comment': [comment]})
        df_comments.to_excel(writer, sheet_name='Voices Comment', index=False)
        worksheet = writer.sheets['Voices Comment']
        worksheet.set_row(1, 310)
        worksheet.write('B1', 'Word Cloud') 
        worksheet.write('A1', 'Voices Comment')
        wrap_format = writer.book.add_format({'text_wrap': True})
        worksheet.set_column('A:A', 60, wrap_format)
        worksheet.set_column('B:B', 80)

        wordcloud_path = 'C:/Users/masay/Documents/pandas/Step3/Step3-2/newproject/backend/static/images/wordcloud.png'
        worksheet.insert_image('B1', wordcloud_path, {'x_scale': 0.2, 'y_scale': 0.2, 'x_offset': 15, 'y_offset': 10})

    output.seek(0)
    return send_file(output, as_attachment=True, download_name="report.xlsx")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
