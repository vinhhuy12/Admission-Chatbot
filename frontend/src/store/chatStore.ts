/**
 * Chat Store using Zustand
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { chatAPI, ChatMessage, ChatQueryResponse } from '@/lib/api'

export interface Message extends ChatMessage {
  id: string
  isLoading?: boolean
  error?: string
  sources?: ChatQueryResponse['sources']
  metadata?: ChatQueryResponse['metadata']
}

interface ChatState {
  messages: Message[]
  conversationId: string | null
  userId: string
  isLoading: boolean
  error: string | null

  // Actions
  sendMessage: (content: string) => Promise<void>
  clearMessages: () => void
  setConversationId: (id: string | null) => void
  setUserId: (id: string) => void
  loadConversationHistory: (conversationId: string) => Promise<void>
  saveConversationToLocal: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      conversationId: null,
      userId: `user_${Date.now()}`,
      isLoading: false,
      error: null,

      sendMessage: async (content: string) => {
        const { conversationId, userId } = get()

        // Add user message
        const userMessage: Message = {
          id: `msg_${Date.now()}`,
          role: 'user',
          content,
          timestamp: new Date().toISOString(),
        }

        set((state) => ({
          messages: [...state.messages, userMessage],
          isLoading: true,
          error: null,
        }))

        // Add loading assistant message
        const loadingMessage: Message = {
          id: `msg_${Date.now() + 1}`,
          role: 'assistant',
          content: '',
          isLoading: true,
          timestamp: new Date().toISOString(),
        }

        set((state) => ({
          messages: [...state.messages, loadingMessage],
        }))

        try {
          // Call API
          const response = await chatAPI.sendQuery({
            query: content,
            conversation_id: conversationId || undefined,
            user_id: userId,
          })

          // Update assistant message with response
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === loadingMessage.id
                ? {
                    ...msg,
                    content: response.answer,
                    isLoading: false,
                    sources: response.sources,
                    metadata: response.metadata,
                    error: response.metadata?.save_warning,
                  }
                : msg
            ),
            conversationId: response.conversation_id,
            isLoading: false,
          }))

          // Save conversation to localStorage for sidebar
          setTimeout(() => get().saveConversationToLocal(), 100)
        } catch (error: any) {
          // Update assistant message with error
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === loadingMessage.id
                ? {
                    ...msg,
                    content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.',
                    isLoading: false,
                    error: error.message,
                  }
                : msg
            ),
            isLoading: false,
            error: error.message,
          }))
        }
      },

      clearMessages: () => {
        set({
          messages: [],
          conversationId: null,
          error: null,
        })
      },

      setConversationId: (id: string | null) => {
        set({ conversationId: id })
      },

      setUserId: (id: string) => {
        set({ userId: id })
      },

      loadConversationHistory: async (conversationId: string) => {
        set({ isLoading: true, error: null })

        try {
          const response = await chatAPI.getConversationHistory(conversationId)

          // Convert API messages to store format
          const messages: Message[] = response.messages.map((msg) => ({
            id: msg.message_id,
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp,
            sources: msg.sources,
          }))

          set({
            messages,
            conversationId,
            isLoading: false,
          })
        } catch (error: any) {
          set({
            messages: [],
            isLoading: false,
            error: error.message,
          })
          throw error
        }
      },

      saveConversationToLocal: () => {
        const { messages, conversationId } = get()
        if (!conversationId || messages.length === 0) return

        // Save conversation summary to localStorage for sidebar
        const userConversations = JSON.parse(localStorage.getItem('user-conversations') || '[]')
        const lastUserMessage = messages.filter(m => m.role === 'user').pop()

        const conversationSummary = {
          id: conversationId,
          title: lastUserMessage?.content.slice(0, 50) + '...' || 'Cuộc trò chuyện mới',
          lastMessage: messages[messages.length - 1]?.content.slice(0, 100) + '...' || '',
          timestamp: new Date().toISOString(),
          messageCount: messages.length,
        }

        // Update or add conversation
        const existingIndex = userConversations.findIndex((c: any) => c.id === conversationId)
        if (existingIndex >= 0) {
          userConversations[existingIndex] = conversationSummary
        } else {
          userConversations.unshift(conversationSummary)
        }

        // Keep only last 50 conversations
        if (userConversations.length > 50) {
          userConversations.splice(50)
        }

        localStorage.setItem('user-conversations', JSON.stringify(userConversations))
      },
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        conversationId: state.conversationId,
        userId: state.userId,
      }),
    }
  )
)

