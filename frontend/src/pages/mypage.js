import Link from 'next/link';

const MyPage = () => {
    return (
        <>
            <nav className="bg-gray py-4 shadow-sm">
                <div className="container mx-auto px-4 flex justify-between items-center">
                    <Link href="/" className="text-blue-500 hover:text-blue-700 font-semibold">ホーム</Link> 
                </div>
            </nav>
            <div className="container mx-auto px-4">
                <h1 className="text-xl font-bold mt-5">マイページ</h1>
            </div>
        </>
    );
};

export default MyPage;
