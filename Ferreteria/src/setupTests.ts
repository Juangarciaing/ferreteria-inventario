import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Polyfill for TextEncoder/TextDecoder (needed for react-router-dom)
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

// Mock de react-hot-toast
global.jest = global.jest || ({} as any);

const mockToast = {
  success: () => {},
  error: () => {},
  loading: () => {},
  dismiss: () => {},
};

// Mock de localStorage
const localStorageMock = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {},
  clear: () => {},
  length: 0,
  key: () => null,
};
Object.defineProperty(global, 'localStorage', { value: localStorageMock });

// Mock de window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Mock de IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
  takeRecords() { return []; }
  root = null;
  rootMargin = '';
  thresholds = [];
} as any;

// Global mock for lib/api module - must be after jest-dom import
jest.mock('./lib/api', () => ({
  apiClient: {
    get: jest.fn(() => Promise.resolve({ data: [] })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
    put: jest.fn(() => Promise.resolve({ data: {} })),
    delete: jest.fn(() => Promise.resolve({ data: {} })),
    authFetch: jest.fn(() => Promise.resolve({ data: {} })),
  },
  TokenManager: {
    getToken: jest.fn(() => 'mock-token'),
    setToken: jest.fn(),
    removeToken: jest.fn(),
    getUser: jest.fn(() => null),
    setUser: jest.fn(),
    removeUser: jest.fn(),
    clear: jest.fn(),
  }
}));
