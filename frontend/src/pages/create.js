import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const CreatePage = () => {
    // State and hooks
    const [emotion, setEmotion] = useState('');
    const [title, setTitle] = useState('');
    const [body, setBody] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [chatInput, setChatInput] = useState('');
    const [showModal, setShowModal] = useState(false);
    const router = useRouter();

    const emotionMessages = {
        1: "嬉しいことがあったようですね。ぜひ嬉しい気持ちをシェアしてください！",
        2: "ぜひ何があったのか話してくれませんか？力になりたいです。",
        3: "ぜひ何があったのか話してくれませんか？力になりたいです。",
        4: "嬉しいことがあったようですね。ぜひ嬉しい気持ちをシェアしてください！",
        5: "もやもやしていることがありますか？なんでも相談してください。",
        6: "何か悩み事がありますか？なんでも相談してください。"
    };

    const emotions = [
        { label: "喜（Joy）", img: "/joy.png" },
        { label: "怒（Angry）", img: "/angry.png" },
        { label: "悲（Sad）", img: "/sad.png" },
        { label: "楽（Happy）", img: "/happy.png" },
        { label: "心配・困った（Worried）", img: "/worried.png" },
        { label: "複雑（Mixed）", img: "/mixed.png" }
    ];

    // Event handlers
    const [message, setMessage] = useState('');
    const handleSubmit = async (e) => {
        e.preventDefault();
        const postData = { emotion, title, body };
        try {
            const response = await fetch('http://127.0.0.1:5000/api/posts/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(postData)
            });
            const data = await response.json();
            if (response.ok) {
                setMessage('投稿されました');
                router.push('/');
            } else {
                setMessage('投稿できませんでした: ' + data.message);
            }
        } catch (error) {
            console.error('Error creating post:', error);
            setMessage('投稿に失敗しました: システムエラー');
        }
    };

    const handleChat = async () => {
        if (chatInput) {
            addMessage(chatInput, 'user');  // ユーザーのメッセージを履歴に追加
            setBody(chatInput);  // bodyのステートを更新
    
            try {
                const response = await fetch('http://127.0.0.1:5000/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: chatInput })
                });
    
                const data = await response.json();
                if (response.ok) {
                    addMessage(data.response, 'bot');  // GPTからの応答を履歴に追加
                } else {
                    addMessage('エラーが発生しました。もう一度お試しください。', 'bot');
                }
            } catch (error) {
                console.error('Chat API error:', error);
                addMessage('通信エラーが発生しました。', 'bot');
            }
    
            setChatInput('');  // 入力フィールドをクリア
        }
    };
    

    const continueChat = async () => {
        if (chatInput) {
            // ユーザーの入力を履歴に追加
            addMessage(chatInput, 'user');
    
            try {
                const response = await fetch('http://127.0.0.1:5000/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: chatInput })
                });
    
                const data = await response.json();
                if (response.ok) {
                    addMessage(data.response, 'bot');  // GPTからの応答を履歴に追加
                    setChatInput('');  // 入力フィールドをクリア
                } else {
                    addMessage('エラーが発生しました。もう一度お試しください。', 'bot');
                }
            } catch (error) {
                console.error('Chat API error:', error);
                addMessage('通信エラーが発生しました。', 'bot');
            }
        }
    };

    const addMessage = (text, sender) => {
        setChatHistory(prevHistory => [...prevHistory, { text, sender }]);
    };

    const openModal = () => {
        const initialMessage = emotionMessages[emotion];
        if (initialMessage) {
            addMessage(initialMessage, 'bot');
        }
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setChatHistory([]);
    };

    return (
        <div>
            <nav className="bg-gray py-4 shadow-sm">
                <div className="container mx-auto px-4 flex justify-between items-center">
                    <Link href="/" className="text-blue-500 hover:text-blue-700 font-semibold">ホーム</Link>
                </div>
            </nav>
            <div className="container mx-auto px-4">
                <form onSubmit={handleSubmit}>
                <h1 className="text-xl font-bold mt-5 mb-8">今の気持ちについて話してみる</h1>
                    <div className="mb-4 flex flex-wrap justify-start items-center">
                        {emotions.map((emotion, index) => (
                            <label key={index} className="flex flex-col items-center justify-center mr-4 mb-4">
                                <img src={emotion.img} alt={emotion.label} className="mb-2 w-20 h-20" />
                                <div>
                                    <input
                                        type="radio"
                                        name="emotion"
                                        value={index + 1}
                                        onChange={() => setEmotion(index + 1)}
                                        className="form-radio"
                                    />
                                    <span className="ml-2">{emotion.label}</span>
                                </div>
                            </label>
                        ))}
                    </div>
                    <div className="mb-4">
                        <label htmlFor="title" className="block text-sm font-medium text-gray-700">タイトル</label>
                        <input type="text" name="title" id="title" onChange={e => setTitle(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
                    </div>
                    <div className="mb-4">
                        <label htmlFor="body" className="block text-sm font-medium text-gray-700">内容</label>
                        <input type="text" name="body" id="body" value={body} onChange={e => setBody(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
                    </div>
                    <button type="submit" className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-gray-500 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500">
                        投稿します
                    </button>
                    <button type="button" className="ml-4 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-500 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:transparent bg-gradient-to-r from-blue-500 to-teal-400" onClick={openModal}>
                        Voicesと対話する
                    </button>
                </form>
                {showModal && (
                    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex justify-center items-center">
                        <div className="bg-white p-5 rounded-lg" style={{ maxWidth: '50%', width: 'auto' }}>
                            <div className="flex justify-between items-center">
                                <h2 className="text-lg">Voicesとの対話</h2>
                                <button onClick={closeModal} className="text-gray-500 hover:text-gray-800">閉じる</button>
                            </div>
                            <div className="mt-4 max-h-96 overflow-y-auto">
                                {chatHistory.map((msg, index) => (
                                    <div key={index} className={`message-box ${msg.sender === 'user' ? 'my-message' : 'ai-message'}`}>
                                        <div className="chat-text">{msg.text}</div>
                                    </div>
                                ))}
                            </div>
                            <textarea className="w-full mt-2 p-2 border rounded" value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="メッセージを入力..."></textarea>
                            <button onClick={handleChat} className="mt-2 bg-gray-500 hover:bg-gray-700 text-white font-bold py-1 px-2 rounded mr-4">送信する</button>
                            <button onClick={continueChat} className="mt-2 transparent bg-gradient-to-r from-blue-500 to-teal-400 hover:transparent bg-gradient-to-r from-blue-500 to-teal-400 text-white font-bold py-1 px-2 rounded">対話を続ける</button>
                            <div className="message">{message && <p>{message}</p>}</div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CreatePage;
