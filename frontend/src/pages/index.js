import Link from 'next/link';

export default function Home() {
    return (
        <div className="container mx-auto p-10"> {/* コンテナにマージンとパディングを追加 */}
            <h1 className="text-8xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-teal-400 text-center mb-20">Voices</h1> {/* タイトルのサイズを更に大きくする */}
            <div className="flex flex-col items-center space-y-12"> {/* ボタン間のスペースを更に広げる */}
                <Link href="/mypage">
                    <button className="bg-gray-200 text-black font-bold py-12 px-20 rounded shadow-lg hover:bg-gray-300 transition-colors text-3xl" style={{ width: '1152px' }}>マイページ</button>
                </Link>
                <Link href="/create">
                    <button className="bg-gray-200 text-black font-bold py-12 px-20 rounded shadow-lg hover:bg-gray-300 transition-colors text-3xl" style={{ width: '1152px' }}>今の気持ちについて話してみる</button>
                </Link>
                <Link href="/check">
                    <button className="bg-gray-200 text-black font-bold py-12 px-20 rounded shadow-lg hover:bg-gray-300 transition-colors text-3xl" style={{ width: '1152px' }}>経営層からの意見の確認</button>
                </Link>
                <Link href="/login">
                    <button className="bg-gray-200 text-black font-bold py-12 px-20 rounded shadow-lg hover:bg-gray-300 transition-colors text-3xl" style={{ width: '1152px' }}>ログアウト</button>
                </Link>
            </div>
        </div>
    );
}
