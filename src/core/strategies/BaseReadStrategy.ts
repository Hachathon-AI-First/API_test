/**
 * Interface for read strategies that provide paginated data access.
 *
 * Implementations should perform the query/read operation and return
 * an object containing the result rows (`data`) and the total number
 * of available items (`total`). This interface is intentionally generic
 * so concrete strategies can accept implementation-specific `params`.
 */
export interface BaseReadStrategy {
    find(params: any, log: any): Promise<{ data: any[]; total: number }>;
}