import type {
    LoginCredentials,
    RegisterCredentials,
    PersonalDetails,
    Preferences,
    HealthConditions,
    UpdatePasswordData,
    ChatMessage,
    ChatResponse,
    AuthStatus,
} from './types';
import { apiCache, CACHE_KEYS } from './apiCache';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchData<T>(
    url: string,
    method: string = 'GET',
    body: unknown = null,
    cacheKey?: string
): Promise<T> {
    // Check cache for GET requests
    if (method === 'GET' && cacheKey) {
        const cachedData = apiCache.get<T>(cacheKey);
        if (cachedData) {
            return cachedData;
        }
    }

    const options: RequestInit = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_URL}${url}`, options);

    if (!response.ok) {
        let errorMessage = response.statusText;
        try {
            const error = await response.json();
            errorMessage = error.detail || error.message || errorMessage;
        } catch {
            // If parsing JSON fails, fallback to statusText
        }
        throw new Error(errorMessage);
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return {} as T;
    }

    try {
        const data = await response.json();

        // Cache the response for GET requests
        if (method === 'GET' && cacheKey) {
            apiCache.set(cacheKey, data);
        }

        return data;
    } catch {
        // Handle cases where response is not JSON
        throw new Error('Invalid response format');
    }
}

// Authentication APIs
export const checkLoginStatus = () =>
    fetchData<AuthStatus>('/check-login/', 'GET', null, CACHE_KEYS.AUTH_STATUS);

export const login = (credentials: LoginCredentials) =>
    fetchData('/login/', 'POST', credentials);

export const register = (credentials: RegisterCredentials) =>
    fetchData('/register/', 'POST', credentials);

export const logout = () => {
    apiCache.clear(); // Clear all cache on logout
    return fetchData('/logout/', 'POST');
};

// Personal Details APIs
export const getPersonalDetails = () =>
    fetchData<PersonalDetails>('/personal-details/', 'GET', null, CACHE_KEYS.PERSONAL_DETAILS);

export const savePersonalDetails = async (data: PersonalDetails) => {
    apiCache.invalidate(CACHE_KEYS.PERSONAL_DETAILS); // Invalidate cache before saving
    return fetchData('/personal-details/', 'POST', data);
};

// Preferences APIs
export const getPreferences = () =>
    fetchData<Preferences>('/preferences/', 'GET', null, CACHE_KEYS.PREFERENCES);

export const savePreferences = async (data: Preferences) => {
    apiCache.invalidate(CACHE_KEYS.PREFERENCES); // Invalidate cache before saving
    return fetchData('/preferences/', 'POST', data);
};

// Health Conditions APIs
export const getHealthConditions = () =>
    fetchData<HealthConditions>('/health-conditions/', 'GET', null, CACHE_KEYS.HEALTH_CONDITIONS);

export const saveHealthConditions = async (data: HealthConditions) => {
    apiCache.invalidate(CACHE_KEYS.HEALTH_CONDITIONS); // Invalidate cache before saving
    return fetchData('/health-conditions/', 'POST', data);
};

// Account Settings APIs
export const updatePassword = (data: UpdatePasswordData) =>
    fetchData('/update-password/', 'PUT', data);

// Chat APIs
export const sendChatMessage = (message: string) =>
    fetchData<ChatResponse>('/chat/', 'POST', { message });

