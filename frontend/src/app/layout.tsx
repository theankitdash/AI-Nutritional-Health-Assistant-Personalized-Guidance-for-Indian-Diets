import type { Metadata } from 'next';
import { AuthProvider } from '@/contexts/AuthContext';
import '@/styles/globals.css';

export const metadata: Metadata = {
    title: 'Nutrify-Health',
    description: 'AI Nutritional Health Assistant - Personalized Guidance for Indian Diets',
    icons: {
        icon: 'https://cdn-icons-png.flaticon.com/128/9756/9756984.png',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body>
                <AuthProvider>
                    {children}
                </AuthProvider>
            </body>
        </html>
    );
}
