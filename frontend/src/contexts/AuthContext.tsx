'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { checkLoginStatus, login as apiLogin, logout as apiLogout, register as apiRegister } from '@/lib/api';
import type { LoginCredentials, RegisterCredentials } from '@/lib/types';

interface AuthContextType {
    isAuthenticated: boolean;
    loading: boolean;
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (credentials: RegisterCredentials) => Promise<void>;
    logout: () => Promise<void>;
    checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    const checkAuth = async () => {
        try {
            const status = await checkLoginStatus();
            setIsAuthenticated(status.isAuthenticated);
        } catch (error) {
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    const login = async (credentials: LoginCredentials) => {
        await apiLogin(credentials);
        setIsAuthenticated(true);
    };

    const register = async (credentials: RegisterCredentials) => {
        await apiRegister(credentials);
        setIsAuthenticated(true);
    };

    const logout = async () => {
        await apiLogout();
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated,
                loading,
                login,
                register,
                logout,
                checkAuth,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
