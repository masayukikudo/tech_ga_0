import React, { useEffect, useState } from 'react';
import Link from 'next/link';

const CheckPage = () => {
    const [posts, setPosts] = useState([]);
    const [editPostId, setEditPostId] = useState(null);
    const [editFormData, setEditFormData] = useState({ title: '', body: '' });

    useEffect(() => {
        fetch('http://127.0.0.1:5000/api/posts')
            .then(response => response.json())
            .then(data => setPosts(data))
            .catch(error => console.error('Error fetching posts:', error));
    }, []);

    const handleEditClick = (post) => {
        setEditPostId(post.id);
        setEditFormData({ title: post.title, body: post.body });
    };

    const handleEditChange = (e) => {
        const { name, value } = e.target;
        setEditFormData({
            ...editFormData,
            [name]: value
        });
    };

    const handleUpdateClick = async (postId) => {
        const updatedPost = {
            id: postId,
            title: editFormData.title,
            body: editFormData.body
        };

        const res = await fetch(`http://127.0.0.1:5000/api/posts/${postId}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedPost)
        });

        const data = await res.json();
        if (res.ok) {
            const updatedPosts = posts.map(post => (post.id === postId ? { ...post, ...updatedPost } : post));
            setPosts(updatedPosts);
            setEditPostId(null);
            console.log(data.message);
        } else {
            throw new Error(data.message);
        }
    };

    const handleDeleteClick = async (postId) => {
        try {
            const res = await fetch(`http://127.0.0.1:5000/api/posts/${postId}/delete`, {
                method: 'DELETE',
            });
            const data = await res.json();
            if (res.ok) {
                setPosts(posts.filter(post => post.id !== postId));
                console.log(data.message);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Failed to delete the post:', error);
        }
    };

    const handleLikeClick = async (postId) => {
        try {
            const res = await fetch(`http://127.0.0.1:5000/api/posts/${postId}/like`, {
                method: 'POST',
            });
            const data = await res.json();
            if (res.ok) {
                const updatedPosts = posts.map(post => post.id === postId ? { ...post, likes: data.likes } : post);
                setPosts(updatedPosts);
                console.log(data.message);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Failed to like the post:', error);
        }
    };

    return (
        <div className="container mx-auto px-4">
            <nav className="bg-gray py-4 shadow-sm">
                <div className="container mx-auto px-4 flex justify-between items-center">
                    <Link href="/" className="text-blue-500 hover:text-blue-700 font-semibold">ホーム</Link>
                </div>
            </nav>
            <h1 className="text-xl font-bold my-4">経営層からの言葉の確認</h1>
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">タイトル</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">本文</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">経営層からの言葉</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">イイネ</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">アクション</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {posts.map((post) => (
                        <tr key={post.id}>
                            <td className="px-6 py-4 whitespace-nowrap">
                                {editPostId === post.id ? (
                                    <input type="text" name="title" value={editFormData.title} onChange={handleEditChange} className="w-full" />
                                ) : (
                                    post.title
                                )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                {editPostId === post.id ? (
                                    <input type="text" name="body" value={editFormData.body} onChange={handleEditChange} className="w-full" />
                                ) : (
                                    post.body
                                )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">{post.manager_comment}</td>
                            <td className="px-6 py-4 whitespace-nowrap">{post.likes}
                                <button onClick={() => handleLikeClick(post.id)} className="ml-2 bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded">いいね</button>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap flex space-x-4">
                                {editPostId === post.id ? (
                                    <button onClick={() => handleUpdateClick(post.id)} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded">更新</button>
                                ) : (
                                    <>
                                        <button onClick={() => handleEditClick(post)} className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-1 px-2 rounded">編集</button>
                                        <button onClick={() => handleDeleteClick(post.id)} className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded">削除</button>
                                    </>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default CheckPage;
