/**
 * Tests para el componente App
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

// Mock del AuthContext
jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: null,
    loading: false,
    signIn: jest.fn(),
    signOut: jest.fn(),
    isAdmin: () => false
  })
}));

// Mock de las páginas
jest.mock('../pages/Login', () => {
  return function MockLogin() {
    return <div data-testid="login-page">Login Page</div>;
  };
});

jest.mock('../pages/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard-page">Dashboard Page</div>;
  };
});

describe('App Component', () => {
  test('renders login page when user is not authenticated', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    expect(screen.getByTestId('login-page')).toBeInTheDocument();
  });

  test('renders dashboard when user is authenticated', () => {
    // Mock del AuthContext con usuario autenticado
    jest.doMock('../contexts/AuthContext', () => ({
      useAuth: () => ({
        user: { id: 1, nombre: 'Test User', email: 'test@test.com', rol: 'vendedor' },
        loading: false,
        signIn: jest.fn(),
        signOut: jest.fn(),
        isAdmin: () => false
      })
    }));

    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
  });
});
