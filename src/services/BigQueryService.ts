import { BigQueryRepository } from "../repositories/BigQueryRepository.js";
import { Logger } from "pino";

/**
 * Service that exposes methods to fetch messages stored in BigQuery.
 *
 * This class delegates the actual BigQuery interaction to a
 * provided `BigQueryRepository` instance, keeping service logic
 * focused on orchestration and input shaping.
 *
 * Example:
 * const svc = new BigQueryService(repo);
 * const rows = await svc.fetchMessages(1, 100, logger);
 */
export class BigQueryService {
    private repository: BigQueryRepository;

    /**
     * Create a new BigQueryService.
     * @param repository - Repository responsible for BigQuery operations.
     */
    constructor(repository: BigQueryRepository) {
        this.repository = repository;
    }

    /**
     * Fetch paginated messages from BigQuery via the repository.
     *
     * @param page - Page number (1-based) to retrieve.
     * @param limit - Number of items per page.
     * @param log - Pino logger instance used by the repository for logging.
     * @returns Repository result (typically a list of message records) as returned by `getMessages`.
     */
    async fetchData(page: number, limit: number, log: Logger) {
        return this.repository.getData(page, limit, log);
    }
}