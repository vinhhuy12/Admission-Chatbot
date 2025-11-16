/**
 * Chat Message Component
 */

'use client'

import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { User, Bot, Copy, Check } from 'lucide-react'
import { Message } from '@/store/chatStore'
import clsx from 'clsx'

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = React.useState(false)
  const isUser = message.role === 'user'

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div
      className={clsx(
        'flex gap-3 p-4 rounded-lg transition-colors',
        isUser
          ? 'bg-primary-50 dark:bg-primary-900/20 ml-auto max-w-[80%]'
          : 'bg-gray-50 dark:bg-gray-800/50 mr-auto max-w-[90%]'
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser
            ? 'bg-primary-500 text-white'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
        )}
      >
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Role Label */}
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
            {isUser ? 'Bạn' : 'Trợ lý tư vấn'}
          </span>
          {!isUser && !message.isLoading && (
            <button
              onClick={handleCopy}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              title="Sao chép"
            >
              {copied ? <Check size={14} /> : <Copy size={14} />}
            </button>
          )}
        </div>

        {/* Message Content */}
        {message.isLoading ? (
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-sm text-gray-500">Đang suy nghĩ...</span>
          </div>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Error or Warning */}
        {message.error && (
          <div className={clsx(
            "mt-2 text-xs",
            message.error.includes('not saved')
              ? "text-yellow-600 dark:text-yellow-400"
              : "text-red-500 dark:text-red-400"
          )}>
            {message.error.includes('not saved') ? '⚠️' : '❌'} {message.error}
          </div>
        )}

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <details className="text-xs">
              <summary className="cursor-pointer text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 font-medium">
                📚 Nguồn tham khảo ({message.sources.length})
              </summary>
              <div className="mt-2 space-y-2">
                {message.sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="p-2 bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700"
                  >
                    <div className="font-medium text-gray-700 dark:text-gray-300">
                      {source.question || 'N/A'}
                    </div>
                    {source.answer && (
                      <div className="text-gray-600 dark:text-gray-400 mt-1">
                        {source.answer.substring(0, 150)}...
                      </div>
                    )}
                    {source.score !== undefined && (
                      <div className="text-gray-400 dark:text-gray-500 mt-1">
                        Độ liên quan: {(source.score * 100).toFixed(1)}%
                      </div>
                    )}
                    {source.article && (
                      <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                        📄 {source.article}
                      </div>
                    )}
                    {source.document && (
                      <div className="text-xs text-gray-400 dark:text-gray-500">
                        📚 {source.document}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </details>
          </div>
        )}

        {/* Metadata */}
        {message.metadata && (
          <div className="mt-2 text-xs text-gray-400 dark:text-gray-500">
            {message.metadata.total_time && (
              <span>⏱️ {message.metadata.total_time.toFixed(2)}s</span>
            )}
            {message.metadata.tokens_used && (
              <span className="ml-2">
                🔤 {message.metadata.tokens_used.total} tokens
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

