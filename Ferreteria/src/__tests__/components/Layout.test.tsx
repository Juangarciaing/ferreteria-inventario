/**
 * Tests para el componente Layout
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../../components/Layout';

// Mock del AuthContext
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, nombre: 'Test User', email: 'test@test.com', rol: 'admin' },
    loading: false,
    signIn: jest.fn(),
    signOut: jest.fn(),
    isAdmin: () => true
  })
}));

// Mock del NotificationCenter
jest.mock('../../components/NotificationCenter', () => {
  return function MockNotificationCenter({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    return isOpen ? (
      <div data-testid="notification-center">
        <button onClick={onClose}>Cerrar</button>
      </div>
    ) : null;
  };
});

describe('Layout Component', () => {
  test('renders layout with navigation', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div data-testid="test-content">Test Content</div>
        </Layout>
      </BrowserRouter>
    );
    
    expect(screen.getByText('Ferretería Control')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Productos')).toBeInTheDocument();
    expect(screen.getByText('Categorías')).toBeInTheDocument();
    expect(screen.getByTestId('test-content')).toBeInTheDocument();
  });

  test('shows admin navigation for admin users', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    );
    
    expect(screen.getByText('Usuarios')).toBeInTheDocument();
    expect(screen.getByText('Auditoría')).toBeInTheDocument();
    expect(screen.getByText('Configuración')).toBeInTheDocument();
  });

  test('opens notification center when bell icon is clicked', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    );
    
    const bellButton = screen.getByRole('button', { name: /notificaciones/i });
    fireEvent.click(bellButton);
    
    expect(screen.getByTestId('notification-center')).toBeInTheDocument();
  });

  test('closes notification center when close button is clicked', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    );
    
    const bellButton = screen.getByRole('button', { name: /notificaciones/i });
    fireEvent.click(bellButton);
    
    expect(screen.getByTestId('notification-center')).toBeInTheDocument();
    
    const closeButton = screen.getByText('Cerrar');
    fireEvent.click(closeButton);
    
    expect(screen.queryByTestId('notification-center')).not.toBeInTheDocument();
  });

  test('shows user information in header', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    );
    
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
  });
});
