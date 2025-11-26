import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from '../types';
import toast from 'react-hot-toast';
import { apiClient, TokenManager } from '../lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Recuperar sesión del token y usuario almacenados
    const initAuth = async () => {
      try {
        const token = TokenManager.getToken();
        const savedUser = TokenManager.getUser();
        
        if (!token || !savedUser) {
          console.log('No hay sesión almacenada - Login requerido');
          setLoading(false);
          return;
        }

        // Validar que el usuario tenga la estructura correcta
        if (savedUser.id && savedUser.nombre && savedUser.email && savedUser.rol) {
          const normalized: User = {
            id: String(savedUser.id),
            nombre: savedUser.nombre,
            email: savedUser.email,
            rol: savedUser.rol,
            created_at: savedUser.created_at || new Date().toISOString(),
          };

          setUser(normalized);
          console.log('Sesión recuperada exitosamente:', normalized);
        } else {
          console.warn('Datos de usuario inválidos, limpiando sesión');
          TokenManager.removeToken();
        }
      } catch (error) {
        console.warn('Error recuperando sesión:', error);
        TokenManager.removeToken();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const signIn = async (email: string, password: string) => {
    try {
      setLoading(true);
      // Autenticación REAL contra backend (guarda token JWT internamente)
      const { user: backendUser } = await apiClient.login({ email, password });

      const normalized: User = {
        id: String(backendUser.id),
        nombre: backendUser.nombre,
        email: backendUser.email,
        rol: backendUser.rol,
        created_at: backendUser.created_at || new Date().toISOString(),
      };

      setUser(normalized);
      console.log('Login exitoso (backend):', normalized);
      toast.success('¡Bienvenido ' + normalized.nombre + '!');
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al iniciar sesión';
      toast.error(message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    try {
      await apiClient.logout();
      setUser(null);
      console.log('Logout exitoso');
      toast.success('Sesión cerrada correctamente');
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al cerrar sesión';
      toast.error(message);
    }
  };

  const isAdmin = user?.rol === 'admin';

  const value: AuthContextType = {
    user,
    loading,
    signIn,
    signOut,
    isAdmin
  };

  console.log('AuthProvider render:', { user, loading, isAdmin });

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};