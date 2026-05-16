import { WebhookMessage } from "../../types/WebhookMessage.js";

/**
 * Interface for publish strategies that handle outgoing webhook messages.
 *
 * Implementations should encapsulate the logic to deliver or store a
 * `WebhookMessage` (for example: publish to Pub/Sub, write to BigQuery, etc.)
 * and return an implementation-specific result.
 *
 * Example:
 * const result = await strategy.publish(message, logger);
 */
export interface BaseStrategy {
    publish(message: WebhookMessage, log: any): Promise<any>;
}