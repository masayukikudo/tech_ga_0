import { useEffect } from 'react';
import { useRouter } from 'next/router';
import styles from '../styles/Home.module.css';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // アニメーションが最も長いものが終了するのを待つ
    const animationDuration = 7000; // 最も長いアニメーションの時間（ミリ秒）

    const timer = setTimeout(() => {
      // アニメーションが終了した後にログインページにリダイレクト
      router.push('/login');
    }, animationDuration);

    // コンポーネントのアンマウント時にタイマーをクリア
    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Voices</h1>
      <p className={styles.paragraph}>エンゲージメントサーベイへようこそ</p>
      {/* リンク要素は削除 */}
    </div>
  );
}
