import { useState, useEffect } from 'react'

function App() {
  // Pythonから取得したデータを保存するステート
  const [wakameData, setWakameData] = useState(null)
  const [loading, setLoading] = useState(true)

  // 画面が表示された瞬間に実行する処理（useEffect）
  useEffect(() => {
    // FastAPIのURLを指定してデータを取得（fetch）
    fetch('http://localhost:8000/api/wakame')
      .then((response) => response.json())
      .then((data) => {
        setWakameData(data)
        setLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching data:', error)
        setLoading(false)
      })
  }, [])

  if (loading) return <p>ワカメを戻しています（読み込み中）...</p>

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>🌱 seaweeds 開発テスト</h1>
      <hr />
      {wakameData ? (
        <div style={{ background: '#f0fdf4', padding: '15px', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
          <h2 style={{ color:'black' }}>現在のワカメの状態</h2>
          <p><strong>ステータス:</strong> {wakameData.status}</p>
          <p><strong>長さ:</strong> {wakameData.length_cm} cm</p>
          <p style={{ color: '#166534', italic: 'true' }}>「 {wakameData.message} 」</p>
        </div>
      ) : (
        <p style={{ color: 'red' }}>FastAPIとの通信に失敗しました。</p>
      )}
    </div>
  )
}

export default App