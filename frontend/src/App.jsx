// src/App.jsx
import React, { useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000/api";

export default function App() {
  // 狀態管理
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("未上傳檔案");
  const [isUploaded, setIsUploaded] = useState(false);

  // Chat 狀態
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "你好！請先在上傳 PDF 講義，接著就可以向我提問！",
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  // Quiz 狀態
  const [quizList, setQuizList] = useState([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState({});

  // 1. 上傳 PDF 處理
  const handleUpload = async () => {
    if (!file) return alert("請先選擇 PDF 檔案！");

    const formData = new FormData();
    formData.append("file", file);

    setUploadStatus("上傳與向量化處理中...");
    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("上傳失敗");

      const data = await res.json();
      setUploadStatus(`成功！共 ${data.total_pages} 頁`);
      setIsUploaded(true);
    } catch (err) {
      setUploadStatus("上傳失敗，請重試");
      alert(err.message);
    }
  };

  // 2. Chat 問答處理
  const handleSendMessage = async () => {
    if (!inputQuery.trim()) return;
    if (!isUploaded) return alert("請先上傳 PDF 講義！");

    const userText = inputQuery;
    setInputQuery("");

    // 加入使用者訊息
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setChatLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userText }),
      });

      if (!res.ok) throw new Error("回答發送失敗");

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.answer },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "抱歉，發生錯誤：" + err.message },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  // 3. 生成 Quiz 處理
  const handleGenerateQuiz = async () => {
    if (!isUploaded) return alert("請先上傳 PDF 講義！");

    setQuizLoading(true);
    try {
      const res = await fetch(`${API_BASE}/quiz`, { method: "POST" });
      if (!res.ok) throw new Error("生成測驗失敗");

      const data = await res.json();
      setQuizList(data.questions || []);
      setSelectedAnswers({});
    } catch (err) {
      alert(err.message);
    } finally {
      setQuizLoading(false);
    }
  };

  // 選擇答案點擊處理
  const handleOptionClick = (qId, optionIdx) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [qId]: optionIdx,
    }));
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>AI 課程 TA 輔助系統</h1>
      </header>

      <div className="main-layout">
        {/* 左側邊欄 */}
        <div className="sidebar">
          {/* 上傳卡片 */}
          <div className="card upload-box">
            <h3>講義上傳</h3>
            <input
              type="file"
              accept=".pdf"
              className="file-input"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button className="btn" onClick={handleUpload}>
              開始上傳解析
            </button>
            <div className={`status-badge ${isUploaded ? "success" : ""}`}>
              {uploadStatus}
            </div>
          </div>

          {/* 測驗區塊 */}
          <div className="card quiz-section">
            <h3>課後測驗生成</h3>
            <button
              className="btn"
              onClick={handleGenerateQuiz}
              disabled={!isUploaded || quizLoading}
            >
              {quizLoading ? "生成中..." : "產生 5 題測驗"}
            </button>

            {quizList.map((q) => {
              const userAns = selectedAnswers[q.id];
              return (
                <div key={q.id} className="quiz-card">
                  <div className="quiz-question">
                    {q.id}. {q.question}
                  </div>
                  {q.options.map((opt, idx) => {
                    let optionClass = "option-btn";
                    if (userAns !== undefined) {
                      if (idx === q.answer) optionClass += " correct";
                      else if (idx === userAns) optionClass += " wrong";
                    }
                    return (
                      <button
                        key={idx}
                        className={optionClass}
                        onClick={() => handleOptionClick(q.id, idx)}
                        disabled={userAns !== undefined}
                      >
                        {opt}
                      </button>
                    );
                  })}
                  {userAns !== undefined && (
                    <div
                      style={{
                        fontSize: "0.8rem",
                        marginTop: "8px",
                        color: "#64748b",
                      }}
                    >
                      💡 {q.explanation} [Page {q.page_citation}]
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* 右側聊天室 */}
        <div className="chat-container">
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                {msg.text}
              </div>
            ))}
            {chatLoading && (
              <div className="message assistant">AI TA 思考中...</div>
            )}
          </div>

          <div className="chat-input-area">
            <input
              type="text"
              className="chat-input"
              placeholder={
                isUploaded ? "請輸入對講義的問題..." : "請先上傳 PDF..."
              }
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              disabled={!isUploaded || chatLoading}
            />
            <button
              className="btn"
              onClick={handleSendMessage}
              disabled={!isUploaded || chatLoading}
            >
              發送
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
