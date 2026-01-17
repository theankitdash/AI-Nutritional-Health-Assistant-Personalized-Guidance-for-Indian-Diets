'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { checkLoginStatus, login as apiLogin, logout as apiLogout, register as apiRegister, getPersonalDetails } from '@/lib/api';
import type { LoginCredentials, RegisterCredentials } from '@/lib/types';

interface AuthContextType {
    isAuthenticated: boolean;
    loading: boolean;
    userName: string;
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (credentials: RegisterCredentials) => Promise<void>;
    logout: () => Promise<void>;
    checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [userName, setUserName] = useState('User');

    const fetchUserName = async () => {
        try {
            const details = await getPersonalDetails();
            setUserName(details.name || 'User');
        } catch (error) {
            console.error('Error fetching user name:', error);
            setUserName('User');
        }
    };

    const checkAuth = async () => {
        try {
            const status = await checkLoginStatus();
            setIsAuthenticated(status.isAuthenticated);
            if (status.isAuthenticated) {
                await fetchUserName();
            }
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
        await fetchUserName();
    };

    const register = async (credentials: RegisterCredentials) => {
        await apiRegister(credentials);
        await apiLogin(credentials);
        setIsAuthenticated(true);
        // Don't fetch user name yet - user needs to fill personal details first
        setUserName('User');
    };

    const logout = async () => {
        await apiLogout();
        setIsAuthenticated(false);
        setUserName('User');
    };

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated,
                loading,
                userName,
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
