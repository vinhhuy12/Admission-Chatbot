/**
 * Main Chat Interface Component
 */

'use client'

import React, { useEffect, useRef, useState } from 'react'
import { useChatStore } from '@/store/chatStore'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import ConversationSidebar from './ConversationSidebar'
import { Trash2, MessageSquare, Menu, X } from 'lucide-react'
import clsx from 'clsx'

export default function ChatInterface() {
  const { messages, isLoading, sendMessage, clearMessages } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (content: string) => {
    await sendMessage(content)
  }

  const handleClear = () => {
    if (confirm('Bạn có chắc muốn xóa toàn bộ lịch sử trò chuyện?')) {
      clearMessages()
    }
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Conversation Sidebar */}
      <ConversationSidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 lg:ml-0">
        {/* Header */}
        <header className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Mobile menu button */}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
              </button>

              <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
                <MessageSquare className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                  Tư vấn tuyển sinh
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Chatbot hỗ trợ tư vấn tuyển sinh đại học
                </p>
              </div>
            </div>

            {messages.length > 0 && (
              <button
                onClick={handleClear}
                className={clsx(
                  'flex items-center gap-2 px-3 py-2 rounded-lg',
                  'text-sm text-gray-600 dark:text-gray-400',
                  'hover:bg-gray-100 dark:hover:bg-gray-700',
                  'transition-colors'
                )}
                title="Xóa lịch sử"
              >
                <Trash2 size={16} />
                <span className="hidden sm:inline">Xóa lịch sử</span>
              </button>
            )}
          </div>
        </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-4 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mb-4">
                <MessageSquare className="text-primary-500" size={40} />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Xin chào! 👋
              </h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-md mb-6">
                Tôi là trợ lý tư vấn tuyển sinh. Tôi có thể giúp bạn về:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl">
                {SUGGESTED_QUESTIONS.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(question)}
                    className={clsx(
                      'p-4 text-left rounded-lg border border-gray-200 dark:border-gray-700',
                      'bg-white dark:bg-gray-800',
                      'hover:border-primary-500 hover:shadow-md',
                      'transition-all duration-200',
                      'text-sm text-gray-700 dark:text-gray-300'
                    )}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0">
        <div className="max-w-5xl mx-auto">
          <ChatInput onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  </div>
  )
}

// Suggested questions
const SUGGESTED_QUESTIONS = [
  'Điều kiện xét tuyển vào đại học là gì?',
  'Học phí đại học bao nhiêu?',
  'Thời gian đăng ký xét tuyển khi nào?',
  'Các ngành học có ở trường là gì?',
]

