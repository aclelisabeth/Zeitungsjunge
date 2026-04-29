// Global state management using Zustand
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// Auth Store
export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,
      
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        try {
          // Will be called from useAuth hook
          set({ isLoading: false });
        } catch (error) {
          set({ error: error.message, isLoading: false });
        }
      },
      
      logout: () => {
        localStorage.removeItem('access_token');
        set({ user: null, token: null });
      },
      
      clearError: () => set({ error: null })
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, token: state.token })
    }
  )
);

// News Store
export const useNewsStore = create((set) => ({
  articles: [],
  selectedArticles: [],
  isLoading: false,
  error: null,
  totalCount: 0,
  
  setArticles: (articles) => set({ articles }),
  setSelectedArticles: (selected) => set({ selectedArticles: selected }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setTotalCount: (count) => set({ totalCount: count }),
  
  addArticle: (article) => 
    set((state) => ({ articles: [article, ...state.articles] })),
  
  removeArticle: (id) => 
    set((state) => ({ 
      articles: state.articles.filter(a => a.id !== id) 
    })),
  
  clearArticles: () => set({ articles: [], selectedArticles: [] })
}));

// Bookmarks Store
export const useBookmarkStore = create((set) => ({
  bookmarks: [],
  bookmarkedIds: new Set(),
  isLoading: false,
  
  setBookmarks: (bookmarks) => {
    const ids = new Set(bookmarks.map(b => b.id));
    set({ bookmarks, bookmarkedIds: ids });
  },
  
  addBookmark: (articleId) => 
    set((state) => ({
      bookmarkedIds: new Set([...state.bookmarkedIds, articleId])
    })),
  
  removeBookmark: (articleId) => 
    set((state) => {
      const newIds = new Set(state.bookmarkedIds);
      newIds.delete(articleId);
      return { bookmarkedIds: newIds };
    }),
  
  isBookmarked: (articleId) => {
    const state = useBookmarkStore.getState();
    return state.bookmarkedIds.has(articleId);
  },
  
  setLoading: (isLoading) => set({ isLoading }),
  
  clearBookmarks: () => set({ bookmarks: [], bookmarkedIds: new Set() })
}));

// Preferences Store
export const usePreferencesStore = create(
  persist(
    (set) => ({
      preferences: {
        preferred_regions: 'global',
        preferred_languages: 'en,de',
        articles_per_page: 15,
        default_time_range: 'today',
        theme: 'light',
        enable_notifications: true
      },
      
      setPreferences: (prefs) => set({ preferences: prefs }),
      updatePreference: (key, value) => 
        set((state) => ({
          preferences: { ...state.preferences, [key]: value }
        })),
      
      getTheme: () => usePreferencesStore.getState().preferences.theme,
      getRegions: () => usePreferencesStore.getState().preferences.preferred_regions,
      getTimeRange: () => usePreferencesStore.getState().preferences.default_time_range
    }),
    {
      name: 'preferences-storage'
    }
  )
);

// UI Store
export const useUIStore = create((set) => ({
  sidebarOpen: true,
  notificationMessage: null,
  notificationType: null,
  
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  showNotification: (message, type = 'info') => {
    set({ notificationMessage: message, notificationType: type });
    setTimeout(() => {
      set({ notificationMessage: null, notificationType: null });
    }, 3000);
  },
  
  clearNotification: () => 
    set({ notificationMessage: null, notificationType: null })
}));
