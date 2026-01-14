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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchData<T>(
    url: string,
    method: string = 'GET',
    body: any = null
): Promise<T> {
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
        const error = await response.json();
        throw new Error(error.detail || response.statusText);
    }

    return response.json();
}

// Authentication APIs
export const checkLoginStatus = () =>
    fetchData<AuthStatus>('/check-login/', 'GET');

export const login = (credentials: LoginCredentials) =>
    fetchData('/login/', 'POST', credentials);

export const register = (credentials: RegisterCredentials) =>
    fetchData('/register/', 'POST', credentials);

export const logout = () =>
    fetchData('/logout/', 'POST');

// Personal Details APIs
export const getPersonalDetails = () =>
    fetchData<PersonalDetails>('/personal-details/', 'GET');

export const savePersonalDetails = (data: PersonalDetails) =>
    fetchData('/personal-details/', 'POST', data);

// Preferences APIs
export const getPreferences = () =>
    fetchData<Preferences>('/preferences/', 'GET');

export const savePreferences = (data: Preferences) =>
    fetchData('/preferences/', 'POST', data);

// Health Conditions APIs
export const getHealthConditions = () =>
    fetchData<HealthConditions>('/health-conditions/', 'GET');

export const saveHealthConditions = (data: HealthConditions) =>
    fetchData('/health-conditions/', 'POST', data);

// Account Settings APIs
export const updatePassword = (data: UpdatePasswordData) =>
    fetchData('/update-password/', 'PUT', data);

// Chat APIs
export const sendChatMessage = (message: string) =>
    fetchData<ChatResponse>('/chat/', 'POST', { message });
