'use client';

import { useState, useEffect } from 'react';

interface UseModalFormOptions<T> {
    fetchData: () => Promise<T>;
    saveData: (data: T) => Promise<any>;
    initialData: T;
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

interface UseModalFormResult<T> {
    formData: T;
    setFormData: React.Dispatch<React.SetStateAction<T>>;
    isLoading: boolean;
    isSaving: boolean;
    error: string | null;
    handleSubmit: (e: React.FormEvent) => Promise<void>;
}

export function useModalForm<T>({
    fetchData,
    saveData,
    initialData,
    isOpen,
    onClose,
    onSuccess,
}: UseModalFormOptions<T>): UseModalFormResult<T> {
    const [formData, setFormData] = useState<T>(initialData);
    const [isLoading, setIsLoading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen) {
            loadData();
        }
    }, [isOpen]);

    const loadData = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await fetchData();
            if (data && Object.keys(data).length > 0) {
                setFormData(data);
            } else {
                setFormData(initialData);
            }
        } catch (err: any) {
            console.error('Error fetching data:', err);
            setError(err.message || 'Failed to load data');
            setFormData(initialData);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setError(null);

        try {
            await saveData(formData);
            onSuccess?.();
            onClose();
        } catch (err: any) {
            console.error('Error saving data:', err);
            setError(err.message || 'Failed to save data');
        } finally {
            setIsSaving(false);
        }
    };

    return {
        formData,
        setFormData,
        isLoading,
        isSaving,
        error,
        handleSubmit,
    };
}
