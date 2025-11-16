/**
 * Conversation Sidebar Component
 */

'use client'

import React, { useState, useEffect } from 'react'
import { useChatStore } from '@/store/chatStore'
import { chatAPI } from '@/lib/api'
import { MessageSquare, Plus, Trash2, Clock } from 'lucide-react'
import clsx from 'clsx'

interface Conversation {
  id: string
  title: string
  lastMessage: string
  timestamp: string
  messageCount: number
}

interface ConversationSidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export default function ConversationSidebar({ isOpen, onToggle }: ConversationSidebarProps) {
  const { conversationId, setConversationId, clearMessages, loadConversationHistory, userId } = useChatStore()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Load conversations list from API
  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    setIsLoading(true)
    try {
      const apiConversations = await chatAPI.getConversations(userId)
      setConversations(apiConversations)

      // Also sync with localStorage for backup
      localStorage.setItem('user-conversations', JSON.stringify(apiConversations))
    } catch (error) {
      console.error('Failed to load conversations from API:', error)

      // Fallback to localStorage
      const savedConversations = localStorage.getItem('user-conversations')
      if (savedConversations) {
        setConversations(JSON.parse(savedConversations))
      }
    } finally {
      setIsLoading(false)
    }
  }

  const createNewConversation = () => {
    clearMessages()
    setConversationId(null) // Set to null for new conversation
    onToggle() // Close sidebar on mobile
  }

  const selectConversation = async (convId: string) => {
    if (convId === conversationId) return

    try {
      setIsLoading(true)
      await loadConversationHistory(convId)
      setConversationId(convId)
      onToggle() // Close sidebar on mobile
    } catch (error) {
      console.error('Failed to load conversation:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const deleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    
    if (!confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) return

    try {
      // Remove from local list
      const updatedConversations = conversations.filter(c => c.id !== convId)
      setConversations(updatedConversations)
      localStorage.setItem('user-conversations', JSON.stringify(updatedConversations))

      // If this is current conversation, create new one
      if (convId === conversationId) {
        createNewConversation()
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return 'Hôm qua'
    } else if (diffDays < 7) {
      return `${diffDays} ngày trước`
    } else {
      return date.toLocaleDateString('vi-VN')
    }
  }

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div className={clsx(
        'fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-50',
        'w-80 transform transition-transform duration-300 ease-in-out',
        isOpen ? 'translate-x-0' : '-translate-x-full',
        'lg:relative lg:translate-x-0 lg:z-auto'
      )}>
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={createNewConversation}
            className={clsx(
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg',
              'bg-primary-500 hover:bg-primary-600 text-white',
              'transition-colors duration-200'
            )}
          >
            <Plus size={20} />
            <span className="font-medium">Cuộc trò chuyện mới</span>
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-gray-500">
              <div className="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-2" />
              Đang tải...
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              <MessageSquare size={48} className="mx-auto mb-3 opacity-50" />
              <p className="text-sm">Chưa có cuộc trò chuyện nào</p>
              <p className="text-xs mt-1">Bắt đầu trò chuyện đầu tiên!</p>
            </div>
          ) : (
            <div className="p-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => selectConversation(conversation.id)}
                  className={clsx(
                    'group flex items-start gap-3 p-3 rounded-lg cursor-pointer',
                    'hover:bg-gray-100 dark:hover:bg-gray-700',
                    'transition-colors duration-200',
                    conversation.id === conversationId && 'bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800'
                  )}
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center">
                    <MessageSquare size={16} className="text-gray-600 dark:text-gray-300" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {conversation.title}
                      </h3>
                      <button
                        onClick={(e) => deleteConversation(conversation.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-all"
                      >
                        <Trash2 size={14} className="text-red-500" />
                      </button>
                    </div>
                    
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate mb-1">
                      {conversation.lastMessage}
                    </p>
                    
                    <div className="flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500">
                      <Clock size={12} />
                      <span>{formatTimestamp(conversation.timestamp)}</span>
                      <span>•</span>
                      <span>{conversation.messageCount} tin nhắn</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
