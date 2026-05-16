import { BaseStrategy } from '../core/strategies/BaseStrategy.js' 
import { WebhookMessage } from '../types/WebhookMessage.js';
import { Logger } from 'pino';

/**
 * Repository that publishes webhook messages using configured strategies.
 *
 * The repository delegates publishing to every `BaseStrategy` instance it
 * holds and collects each strategy's result. This centralises orchestration
 * and keeps strategy implementations isolated and testable.
 *
 * Example:
 * const repo = new WebhookRepository([pubSubStrategy, bigQueryStrategy]);
 * const results = await repo.saveMessage(message, logger);
 */
export class WebhookRepository {
    private strategies: BaseStrategy[];

    /**
     * Create a new WebhookRepository.
     * @param strategies - Array of `BaseStrategy` implementations used to publish messages. Defaults to an empty array.
     */
    constructor(strategies: BaseStrategy[] = []) {
        this.strategies = strategies;
    }

    /**
     * Publish a `WebhookMessage` to all configured strategies and return per-strategy results.
     *
     * - Iterates strategies sequentially and awaits each `publish` call.
     * - Captures the concrete strategy name and the result returned by it.
     *
     * @param message - Normalized webhook message to be published.
     * @param log - Pino logger instance forwarded to strategies for logging.
     * @returns Promise resolving to an array of result objects shaped as `{ strategy: string, result: any }`.
     */
    async saveMessage(message: WebhookMessage, log: Logger): Promise<any[]> {
        const result: any[] = [];

        for (const strategy of this.strategies) {
            const res = await strategy.publish(message, log);
            const strategyName = (strategy as any).constructor.name;

            result.push({
                strategy: strategyName, 
                result: res 
            });
        }
        return result;
    }
}