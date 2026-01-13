'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Header from '@/components/layout/Header';
import Sidebar from '@/components/layout/Sidebar';
import ChatContainer from '@/components/chat/ChatContainer';
import AuthModal from '@/components/modals/AuthModal';
import PersonalDetailsModal from '@/components/modals/PersonalDetailsModal';
import PreferencesModal from '@/components/modals/PreferencesModal';
import HealthConditionsModal from '@/components/modals/HealthConditionsModal';
import AccountSettingsModal from '@/components/modals/AccountSettingsModal';
import styles from '@/styles/components/MainPage.module.css';

export default function Home() {
    const { isAuthenticated, loading } = useAuth();
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [showPersonalDetails, setShowPersonalDetails] = useState(false);
    const [showPreferences, setShowPreferences] = useState(false);
    const [showHealthConditions, setShowHealthConditions] = useState(false);
    const [showAccountSettings, setShowAccountSettings] = useState(false);

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            setShowAuthModal(true);
        }
    }, [isAuthenticated, loading]);

    const handleAuthSuccess = (isRegistration: boolean) => {
        setShowAuthModal(false);
        // Only show personal details modal after registration, not login
        if (isRegistration) {
            setShowPersonalDetails(true);
        }
    };

    if (loading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh'
            }}>
                Loading...
            </div>
        );
    }

    return (
        <>
            {isAuthenticated && (
                <>
                    <Header />
                    <Sidebar
                        onOpenPersonalDetails={() => setShowPersonalDetails(true)}
                        onOpenPreferences={() => setShowPreferences(true)}
                        onOpenHealthConditions={() => setShowHealthConditions(true)}
                        onOpenAccountSettings={() => setShowAccountSettings(true)}
                    />
                    <div className={styles.mainContainer}>
                        <main className={styles.mainContent}>
                            <ChatContainer />
                        </main>
                    </div>
                </>
            )}

            {/* Modals */}
            <AuthModal
                isOpen={showAuthModal}
                onClose={() => setShowAuthModal(false)}
                onAuthSuccess={handleAuthSuccess}
            />
            <PersonalDetailsModal
                isOpen={showPersonalDetails}
                onClose={() => setShowPersonalDetails(false)}
            />
            <PreferencesModal
                isOpen={showPreferences}
                onClose={() => setShowPreferences(false)}
            />
            <HealthConditionsModal
                isOpen={showHealthConditions}
                onClose={() => setShowHealthConditions(false)}
            />
            <AccountSettingsModal
                isOpen={showAccountSettings}
                onClose={() => setShowAccountSettings(false)}
            />
        </>
    );
}
