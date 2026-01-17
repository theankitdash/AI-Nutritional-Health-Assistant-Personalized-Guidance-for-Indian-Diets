// Simple cache implementation for API calls
interface CacheEntry<T> {
    data: T;
    timestamp: number;
    ttl: number; // Time to live in milliseconds
}

class ApiCache {
    private cache: Map<string, CacheEntry<any>> = new Map();

    /**
     * Get data from cache if it exists and is not expired
     */
    get<T>(key: string): T | null {
        const entry = this.cache.get(key);

        if (!entry) {
            return null;
        }

        const now = Date.now();
        const isExpired = now - entry.timestamp > entry.ttl;

        if (isExpired) {
            this.cache.delete(key);
            return null;
        }

        return entry.data as T;
    }

    /**
     * Set data in cache with a TTL (default: 5 minutes)
     */
    set<T>(key: string, data: T, ttl: number = 5 * 60 * 1000): void {
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl,
        });
    }

    /**
     * Remove specific key from cache
     */
    invalidate(key: string): void {
        this.cache.delete(key);
    }

    /**
     * Remove all keys matching a pattern
     */
    invalidatePattern(pattern: RegExp): void {
        const keysToDelete: string[] = [];

        this.cache.forEach((_, key) => {
            if (pattern.test(key)) {
                keysToDelete.push(key);
            }
        });

        keysToDelete.forEach((key) => this.cache.delete(key));
    }

    /**
     * Clear all cache
     */
    clear(): void {
        this.cache.clear();
    }

    /**
     * Get cache size
     */
    size(): number {
        return this.cache.size;
    }
}

// Export singleton instance
export const apiCache = new ApiCache();

// Cache key constants
export const CACHE_KEYS = {
    AUTH_STATUS: 'auth-status',
    PERSONAL_DETAILS: 'personal-details',
    PREFERENCES: 'preferences',
    HEALTH_CONDITIONS: 'health-conditions',
} as const;
