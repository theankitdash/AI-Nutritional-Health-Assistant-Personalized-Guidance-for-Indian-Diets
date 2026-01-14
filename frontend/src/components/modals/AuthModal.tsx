'use client';

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import { useAuth } from '@/contexts/AuthContext';
import { isValidEmail, isStrongPassword } from '@/lib/utils';
import styles from '@/styles/components/Modal.module.css';

interface AuthModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAuthSuccess: (isRegistration: boolean) => void;
}

export default function AuthModal({ isOpen, onClose, onAuthSuccess }: AuthModalProps) {
    const [isRegistering, setIsRegistering] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [emailFeedback, setEmailFeedback] = useState('');
    const [passwordFeedback, setPasswordFeedback] = useState('');
    const [confirmPasswordFeedback, setConfirmPasswordFeedback] = useState('');

    const { login, register } = useAuth();

    const handleUsernameChange = (value: string) => {
        setUsername(value);
        if (isRegistering) {
            if (isValidEmail(value)) {
                setEmailFeedback('Valid email address.');
            } else {
                setEmailFeedback('Please enter a valid email address.');
            }
        }
    };

    const handlePasswordChange = (value: string) => {
        setPassword(value);
        if (isRegistering) {
            if (isStrongPassword(value)) {
                setPasswordFeedback('Strong password.');
            } else {
                setPasswordFeedback(
                    'Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.'
                );
            }
        }
    };

    const handleConfirmPasswordChange = (value: string) => {
        setConfirmPassword(value);
        if (isRegistering) {
            if (value === password) {
                setConfirmPasswordFeedback('Passwords match.');
            } else {
                setConfirmPasswordFeedback('Passwords do not match.');
            }
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (isRegistering) {
            if (password !== confirmPassword) {
                alert('Passwords do not match. Please try again.');
                return;
            }
            if (!isStrongPassword(password)) {
                alert(
                    'Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.'
                );
                return;
            }

            try {
                await register({ email: username, password });
                alert('User registration successful! Please add personal details.');
                onAuthSuccess(true); // true = is a registration
            } catch (error: any) {
                console.error('Error during registration:', error);
                alert(`Registration failed: ${error.message}`);
            }
        } else {
            try {
                await login({ email: username, password });
                alert('Login Successful!');
                onAuthSuccess(false); // false = not a registration
            } catch (error: any) {
                alert(`Error: ${error.message}`);
            }
        }
    };

    const toggleMode = () => {
        setIsRegistering(!isRegistering);
        setUsername('');
        setPassword('');
        setConfirmPassword('');
        setEmailFeedback('');
        setPasswordFeedback('');
        setConfirmPasswordFeedback('');
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={isRegistering ? 'Register' : 'Login'}
        >
            <form onSubmit={handleSubmit}>
                <div className={styles.setting}>
                    <label htmlFor="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => handleUsernameChange(e.target.value)}
                        required
                    />
                    {isRegistering && emailFeedback && (
                        <div
                            className={styles.feedback}
                            style={{
                                color: emailFeedback.includes('Valid') ? 'green' : 'red',
                            }}
                        >
                            {emailFeedback}
                        </div>
                    )}
                </div>

                <div className={styles.setting}>
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => handlePasswordChange(e.target.value)}
                        required
                    />
                    {isRegistering && passwordFeedback && (
                        <div
                            className={styles.feedback}
                            style={{
                                color: passwordFeedback.includes('Strong') ? 'green' : 'red',
                            }}
                        >
                            {passwordFeedback}
                        </div>
                    )}
                </div>

                {isRegistering && (
                    <div className={styles.setting}>
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => handleConfirmPasswordChange(e.target.value)}
                        />
                        {confirmPasswordFeedback && (
                            <div
                                className={styles.feedback}
                                style={{
                                    color: confirmPasswordFeedback.includes('match') ? 'green' : 'red',
                                }}
                            >
                                {confirmPasswordFeedback}
                            </div>
                        )}
                    </div>
                )}

                <button className={styles.button} type="submit">
                    Submit
                </button>
                <button className={styles.button} type="button" onClick={toggleMode}>
                    {isRegistering ? 'Back to Login' : 'Register'}
                </button>
            </form>
        </Modal>
    );
}
