import { BaseReadStrategy } from "../core/strategies/BaseReadStrategy.js";
import { Logger } from "pino";

/**
 * Repository responsible for reading messages using a configured read strategy.
 *
 * This repository delegates pagination and read logic to a provided
 * `BaseReadStrategy` implementation. It centralises validation (ensuring a
 * strategy exists) and forwards the paging options and logger to the strategy.
 *
 * Example:
 * const repo = new BigQueryRepository(bigQueryReadStrategy);
 * const rows = await repo.getMessages(1, 100, logger);
 */
export class BigQueryRepository {
    private readStrategy: BaseReadStrategy;

    /**
     * Create a new BigQueryRepository.
     * @param readStrategy - Strategy implementing read operations (should implement `find`).
     */
    constructor(readStrategy: BaseReadStrategy) {
        this.readStrategy = readStrategy;
    }

    /**
     * Fetch paginated messages via the configured read strategy.
     *
     * @param page - Page number (1-based) to retrieve.
     * @param limit - Number of items per page.
     * @param log - Pino logger instance forwarded to the strategy.
     * @returns The value returned by the strategy's `find` method (implementation-specific).
     * @throws Error when no read strategy is provided.
     */
    async getData(page: number, limit: number, log: Logger ) {
        const strategy = this.readStrategy;

        if (!strategy) {
            log.error('No read strategy provided');
            throw new Error("No read strategy provided");
        }

        return strategy.find({ page, limit }, log);
    }
}