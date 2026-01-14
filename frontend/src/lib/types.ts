// API Types
export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterCredentials extends LoginCredentials { }

export interface PersonalDetails {
    name: string;
    dateofbirth: string;
    gender: 'male' | 'female' | 'other';
    height: number;
    weight: number;
    waist: number;
}

export interface Preferences {
    foodpreference: string;
    snackpreferences: string;
    mealtimings: string;
    cheatdayfrequency: string;
    culturalpreferences: string;
    preferredingredients: string;
    cuisinepreferences: string;
    spicyfoodtolerance: string;
    preferredmealtype: string;
    favoritemeal: string;
    mealfrequency: string;
    sweetpreference: string;
    eatingoutfrequency: string;
    hydrationlevel: number;
    preferreddrinks: string;
    activitylevel: string;
    fitnessgoal: string;
    foodrestrictions: string;
    caffeineintake: string;
    averagesleep: number;
    sleepquality: string;
    supplementusage: string;
    supplementfrequency: string;
}

export interface HealthConditions {
    allergies: string;
    diabetes: string;
    hypertension: string;
    cholesterol: string;
    thyroid: string;
    kidneydisease: string;
    liverdisease: string;
    lactoseintolerance: string;
    glutensensitivity: string;
    pcos?: string;  // Optional - only for female users
    anemia: string;
    osteoporosis: string;
    ibs: string;
    gerd: string;
    gout: string;
    otherconditions: string;
}

export interface UpdatePasswordData {
    current_password: string;
    new_password: string;
}

export interface ChatMessage {
    message: string;
}

export interface ChatResponse {
    bot_response: string;
}

export interface AuthStatus {
    isAuthenticated: boolean;
}
