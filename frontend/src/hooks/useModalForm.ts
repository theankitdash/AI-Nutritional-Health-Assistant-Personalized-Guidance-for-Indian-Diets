'use client';

import { useState, useEffect, useCallback } from 'react';
import type { ApiError } from '@/lib/types';
import { useToast } from '@/contexts/ToastContext';

interface UseModalFormOptions<T> {
    fetchData: () => Promise<T>;
    saveData: (data: T) => Promise<unknown>;
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
    const { showToast } = useToast();

    const loadData = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await fetchData();
            if (data && Object.keys(data as object).length > 0) {
                setFormData(data);
            } else {
                setFormData(initialData);
            }
        } catch (err: unknown) {
            console.error('Error fetching data:', err);
            const message = (err as ApiError).message || (err as Error).message || 'Failed to load data';
            setError(message);
            // Optional: showToast(message, 'error'); // Maybe too noisy on load
            setFormData(initialData);
        } finally {
            setIsLoading(false);
        }
    }, [fetchData, initialData]);

    useEffect(() => {
        if (isOpen) {
            loadData();
        }
    }, [isOpen, loadData]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setError(null);

        try {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const response = await saveData(formData) as any;

            // Show success message from backend
            if (response?.message) {
                showToast(response.message, 'success');
            } else {
                showToast('Data saved successfully!', 'success');
            }

            onSuccess?.();
            onClose();
        } catch (err: unknown) {
            console.error('Error saving data:', err);
            const message = (err as ApiError).message || (err as Error).message || 'Failed to save data';
            setError(message);
            showToast(message, 'error');
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
